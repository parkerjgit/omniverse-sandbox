import asyncio
import carb
import os
import omni.usd

from ..native_bindings import *
from .omni_client_wrapper import OmniClientWrapper
from .context import AssetConverterContext


class AssetConverterFutureWrapper:
    def __init__(self, import_path, output_path, import_context, future, close_stage_and_reopen_if_opened):
        super().__init__()
        self._native_future = future
        self._cancelled = False
        self._import_path = import_path
        self._output_path = output_path
        self._import_context = import_context
        self._is_finished = False
        self._task_done_callbacks = []
        self._close_stage_and_reopen_if_opened = close_stage_and_reopen_if_opened
        self._error_message = ""
        self._status = OmniConverterStatus.OK

    def add_task_done_callback(self, callback):
        if callback not in self._task_done_callbacks:
            self._task_done_callbacks.append(callback)

    def remove_task_done_callback(self, callback):
        if callback in self._task_done_callbacks:
            self._task_done_callbacks.remove(callback)

    def cancel(self):
        if not self._cancelled:
            self._native_future.cancel()
            self._cancelled = True

    def is_cancelled(self):
        return self._cancelled

    def is_finished(self):
        return self._is_finished
    
    def get_status(self):
        return self._status
        
    def get_error_message(self):
        return self._error_message

    def _notify_finished(self):
        for callback in self._task_done_callbacks:
            callback()

    async def wait_until_finished(self):
        if self.is_cancelled() or self.is_finished():
            self._notify_finished()
            return not self.is_cancelled()

        self._status = OmniConverterStatus.OK
        self._error_message = ""
        usd_context = omni.usd.get_context()
        current_stage_url = usd_context.get_stage_url()
        opened = os.path.normpath(self._output_path) == os.path.normpath(current_stage_url)
        if not self._close_stage_and_reopen_if_opened and opened:
            self._error_message = f"Failed to import {self._import_path} as USD since output path {self._output_path} is opened already."
            carb.log_error(self._error_message)
            self._status = OmniConverterStatus.UNKNOWN

            return False

        try:
            if opened:
                await usd_context.close_stage_async()

            async with self._native_future as future:
                status = future.get_status()
                error = future.get_detailed_error()
                if status != OmniConverterStatus.OK:
                    self._error_message = f"Couldn't Import Asset: {self._import_path}, code: {status}, error: {error}"
                    self._status = status
                    carb.log_error(self._error_message)
                    return False

            if opened:
                await usd_context.open_stage_async(self._output_path)

            return True
        finally:
            self._is_finished = True
            AssetConverterTaskManager._task_map.discard(self)
            self._notify_finished()

        return False


class AssetConverterTaskManager:
    _thread_loop = None
    _task_map = set()

    @staticmethod
    def on_startup():
        AssetConverterTaskManager._thread_loop = None
        token = carb.tokens.get_tokens_interface()
        data_dir = token.resolve("${data}")
        cache_dir = os.path.join(data_dir, "omniverse_asset_converter_cache")
        cache_dir = cache_dir.replace("\\", "/")
        carb.log_info(f"Initialize asset converter with cache folder {cache_dir}...")
        OmniAssetConverter.set_cache_folder(cache_dir)
        OmniAssetConverter.set_log_callback(AssetConverterTaskManager._log_print)
        OmniAssetConverter.set_file_callback(
            None,
            AssetConverterTaskManager._asset_converter_binary_write,
            None,
            None,
            None,
            AssetConverterTaskManager._asset_converter_file_copy
        )

    @staticmethod
    def on_shutdown():
        for future_wrapper in AssetConverterTaskManager._task_map:
            future_wrapper.cancel()
        AssetConverterTaskManager._task_map.clear()
        OmniAssetConverter.shutdown()

    @staticmethod
    def remove_task(task):
        AssetConverterContext._task_map.discard(task)

    @staticmethod
    def create_converter_task(
        import_path: str,
        output_path: str,
        progress_callback,
        asset_converter_context: AssetConverterContext = None,
        material_loader=None,
        close_stage_and_reopen_if_opened=False
    ):
        # If not context is provided, creates a default one.
        if not asset_converter_context:
            asset_converter_context = AssetConverterContext()

        future = OmniAssetConverter(
            import_path,
            output_path,
            progress_callback,
            asset_converter_context.ignore_materials,
            asset_converter_context.ignore_animations,
            asset_converter_context.single_mesh,
            asset_converter_context.smooth_normals,
            asset_converter_context.ignore_camera,
            asset_converter_context.export_preview_surface,
            asset_converter_context.support_point_instancer,
            False,
            True,
            asset_converter_context.use_meter_as_world_unit,
            asset_converter_context.create_world_as_default_root_prim,
            asset_converter_context.ignore_light,
            asset_converter_context.embed_textures,
            material_loader=material_loader,
            convert_fbx_to_y_up=asset_converter_context.convert_fbx_to_y_up,
            convert_fbx_to_z_up=asset_converter_context.convert_fbx_to_z_up,
            keep_all_materials=asset_converter_context.keep_all_materials,
            merge_all_meshes=asset_converter_context.merge_all_meshes,
            use_double_precision_to_usd_transform_op=asset_converter_context.use_double_precision_to_usd_transform_op,
            ignore_pivots=asset_converter_context.ignore_pivots,
            disable_instancing=asset_converter_context.disabling_instancing,
            export_hidden_props=asset_converter_context.export_hidden_props,
            baking_scales=asset_converter_context.baking_scales
        )

        wrapper = AssetConverterFutureWrapper(import_path, output_path, asset_converter_context, future, close_stage_and_reopen_if_opened)
        AssetConverterTaskManager._task_map.add(wrapper)

        return wrapper

    @staticmethod
    def _get_thread_loop():
        if not AssetConverterTaskManager._thread_loop:
            AssetConverterTaskManager._thread_loop = asyncio.new_event_loop()

        return AssetConverterTaskManager._thread_loop

    @staticmethod
    def _log_print(message):
        carb.log_info(message)

    @staticmethod
    def _asset_converter_binary_write(path, data):
        return AssetConverterTaskManager._get_thread_loop().run_until_complete(
            OmniClientWrapper.write(path, bytearray(data))
        )
    
    @staticmethod
    def _asset_converter_file_copy(target_path, source_path):
        return AssetConverterTaskManager._get_thread_loop().run_until_complete(
            OmniClientWrapper.copy(source_path, target_path)
        )
