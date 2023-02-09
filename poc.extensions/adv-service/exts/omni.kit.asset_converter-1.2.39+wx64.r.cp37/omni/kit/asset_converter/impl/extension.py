# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import os
import weakref
import omni.ext

from typing import Callable
from functools import partial
from .omni_client_wrapper import OmniClientWrapper
from .context import AssetConverterContext
from .task_manager import AssetConverterTaskManager, AssetConverterFutureWrapper


def get_instance():
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()

    return None


class AssetImporterExtension(omni.ext.IExt):
    def on_startup(self):
        global _global_instance
        _global_instance = weakref.ref(self)
        AssetConverterTaskManager.on_startup()

    def on_shutdown(self):
        global _global_instance
        _global_instance = None
        AssetConverterTaskManager.on_shutdown()

    def create_converter_task(
        self,
        import_path: str,
        output_path: str,
        progress_callback: Callable[[int], int] = None,
        asset_converter_context: AssetConverterContext = AssetConverterContext(),
        material_loader=None,
        close_stage_and_reopen_if_opened: bool = False
    ):
        """
        Creates task to convert import_path to output_path. Currently, it supports
        to convert fbx/obj/glTF to USD, or USD to fbx/obj/glTF.
        
        Snippet to use it:
        >>> import asyncio
        >>> importer omni.kit.asset_converter as converter
        >>> 
        >>> async def convert(...):
        >>>     task_manger = converter.get_instance()
        >>>     task = task_manger.create_converter_task(...)
        >>>     success = await task.wait_until_finished()
        >>>     if not success:
        >>>         detailed_status_code = task.get_status()
        >>>         detailed_status_error_string = task.get_error_message()

        NOTE: It uses FBX SDK for FBX convert and Assimp as fallback backend, so it should support
        all assets that Assimp supports. But only obj/glTF are fully verified.
        
        Args:
            import_path (str): The source asset to be converted. It could also be stage id that's 
                               cached in UsdUtils.StageCache since it supports to export loaded stage.

            output_path (str): The target asset. Asset format is decided by its extension.

            progress_callback(Callable[[int], int]): Progress callback to monitor the progress of
                                                   conversion. The first param is the progress, and
                                                   the second one is the total steps.
            asset_converter_context (omni.kit.asset_converter.AssetConverterContext): Context.

            material_loader (Callable[[omni.kit.asset_conerter.native_bindings.MaterialDescription], None]): You
                                                   can set this to intercept the material loading.
        
            close_stage_and_reopen_if_opened (bool): If the output path has already been opened in the 
                                                     current UsdContext, it will close the current stage, then import
                                                     and re-open it after import successfully if this flag is true. Otherwise,
                                                     it will return False and report errors.
        """

        return AssetConverterTaskManager.create_converter_task(
            import_path, output_path, progress_callback, asset_converter_context, material_loader, close_stage_and_reopen_if_opened
        )
