import os
import carb.tokens
import omni.kit.test
import omni.kit.asset_converter
from pathlib import Path
from pxr import Sdf, Usd


# NOTE: those tests belong to omni.kit.asset_converter extension.
class TestAssetConverter(omni.kit.test.AsyncTestCaseFailOnLogError):
    def get_test_dir(self):
        token = carb.tokens.get_tokens_interface()
        data_dir = token.resolve("${temp}")

        return f"{data_dir}/asset_converter_tests"

    async def setUp(self):
        pass

    async def tearDown(self):
        await omni.client.delete_async(self.get_test_dir())

    async def test_convert_assets_to_usd(self):
        current_path = Path(__file__).parent
        # invalid_mesh.obj includes an invalid mesh that has zero points
        for file in ["cube.fbx", "cube.obj", "cube.gltf"]:
            test_data_path = str(current_path.parent.parent.parent.parent.joinpath("data").joinpath(file))
            converter_manager = omni.kit.asset_converter.get_instance()
            context = omni.kit.asset_converter.AssetConverterContext()
            context.keep_all_materials = True
            context.merge_all_meshes = True
            output_path = self.get_test_dir() + "/test.usd"
            task = converter_manager.create_converter_task(test_data_path, output_path, None, context)
            success = await task.wait_until_finished()
            self.assertTrue(success, f"Failed to convert asset {file}.")
            self.assertTrue(Path(output_path).is_file(), f"Failed to convert asset {file}.")
            await omni.client.delete_async(self.get_test_dir())

    async def test_convert_usd_to_other_formats(self):
        current_path = Path(__file__).parent
        test_data_path = str(current_path.parent.parent.parent.parent.joinpath("data").joinpath("cube.fbx"))
        converter_manager = omni.kit.asset_converter.get_instance()
        context = omni.kit.asset_converter.AssetConverterContext()
        output_path = self.get_test_dir() + "/test.usd"

        # Creates usd firstly
        task = converter_manager.create_converter_task(test_data_path, output_path, None, context)
        success = await task.wait_until_finished()
        self.assertTrue(success)
        self.assertTrue(Path(output_path).is_file())

        for asset_name in ["test.fbx", "test.obj", "test.gltf"]:
            asset_path = self.get_test_dir() + f"/{asset_name}"
            task = converter_manager.create_converter_task(output_path, asset_path, None, context)
            success = await task.wait_until_finished()
            self.assertTrue(success)
            self.assertTrue(Path(asset_path).is_file())
    
    async def test_convert_assets_to_anonymous_layer(self):
        layer = Sdf.Layer.CreateAnonymous()
        current_path = Path(__file__).parent
        for file in ["cube.fbx", "cube.obj", "cube.gltf"]:
            test_data_path = str(current_path.parent.parent.parent.parent.joinpath("data").joinpath(file))
            converter_manager = omni.kit.asset_converter.get_instance()
            context = omni.kit.asset_converter.AssetConverterContext()
            context.keep_all_materials = True
            context.merge_all_meshes = True
            context.baking_scales = True
            task = converter_manager.create_converter_task(test_data_path, layer.identifier, None, context)
            success = await task.wait_until_finished()
            self.assertTrue(success, f"Failed to convert asset {file}.")
            await omni.client.delete_async(self.get_test_dir())
    
    async def test_open_non_usd(self):
        current_path = Path(__file__).parent
        for file in ["cube.fbx", "cube.obj", "cube.gltf"]:
            test_data_path = str(current_path.parent.parent.parent.parent.joinpath("data").joinpath(file))
            self.assertIsNotNone(Usd.Stage.Open(test_data_path))
        
    async def test_overwrite_opened_stage(self):
        current_path = Path(__file__).parent
        output_path = self.get_test_dir() + "/test.usd"
        opened = False
        for i in range(10):
            test_data_path = str(current_path.parent.parent.parent.parent.joinpath("data").joinpath("cube.fbx"))
            converter_manager = omni.kit.asset_converter.get_instance()
            context = omni.kit.asset_converter.AssetConverterContext()
            task = converter_manager.create_converter_task(test_data_path, output_path, None, context, None, True)
            success = await task.wait_until_finished()
            self.assertTrue(success, "Failed to convert asset cube.fbx.")
            # For the first round, opening this stage for next overwrite
            if not opened:
                await omni.usd.get_context().open_stage_async(output_path)
                opened = True

        await omni.client.delete_async(self.get_test_dir())


