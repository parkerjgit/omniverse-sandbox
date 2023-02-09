## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path
import inspect
import os
import platform
import unittest
import glob
import carb
import omni.kit.app
import omni.usd
from omni.kit.test.async_unittest import AsyncTestCase
from pxr import Sdf, UsdGeom, Usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading, set_content_browser_grid_view, get_content_browser_path_item, get_prims


class TestDragDropUSD(AsyncTestCase):
    def verify_dragged_references(self, prim_name, file_path, prims):
        if os.path.splitext(file_path)[1] in [".usd", ".usda", ".usdc", ".fbx", ".gltf", ".obj"]:
            self.assertTrue(len(prims) >= 2)
            self.assertTrue(prims[0].GetPath().pathString == f"/World/{prim_name}")
            self.assertTrue(prims[0].GetPrimPath().pathString == f"/World/{prim_name}")
            external_refs = omni.usd.get_composed_references_from_prim(prims[1])
            self.assertTrue(len(external_refs) == 0)
            external_refs = omni.usd.get_composed_references_from_prim(prims[0])
            self.assertTrue(len(external_refs) >= 1)
            prim_ref = external_refs[0][0]
            self.assertTrue(prim_ref.customData == {})
            self.assertTrue(prim_ref.layerOffset == Sdf.LayerOffset())
            self.assertTrue(prim_ref.primPath == Sdf.Path())
            self.assertTrue(prim_ref.assetPath.lower() == file_path.lower())
        else:
            self.assertTrue(len(prims) == 0)

    async def create_stage(self):
        await omni.usd.get_context().new_stage_async()
        await wait_stage_loading()

        # Create defaultPrim
        usd_context = omni.usd.get_context()
        settings = carb.settings.get_settings()
        default_prim_name = settings.get("/persistent/app/stage/defaultPrimName")
        rootname = f"/{default_prim_name}"
        stage = usd_context.get_stage()
        with Usd.EditContext(stage, stage.GetRootLayer()):
            default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(rootname)).GetPrim()
            stage.SetDefaultPrim(default_prim)

        stage_prims = get_prims(stage)
        return stage, stage_prims

    async def iter_prims_to_drag(self):
        for path in glob.glob(get_test_data_path(__name__, "../*")):
            prim_path = os.path.abspath(path).replace("\\", "/")
            item = await get_content_browser_path_item(prim_path)
            yield item, prim_path

    async def test_l1_drag_drop_usd_viewport(self):
        if inspect.iscoroutinefunction(set_content_browser_grid_view):
            await set_content_browser_grid_view(False)
        else:
            set_content_browser_grid_view(False)

        await ui_test.find("Content").focus()
        viewport = ui_test.find("Viewport")
        await viewport.focus()
        end_pos = viewport.center

        async for item, prim_path in self.iter_prims_to_drag():
            if os.path.splitext(item.path)[1] not in [".usd", ".usda", ".usdc", ".fbx", ".gltf", ".obj"]:
                continue

            # create stage
            stage, stage_prims = await self.create_stage()

            # drag/drop to centre of viewport
            await item.drag_and_drop(end_pos)

            # verify new prims
            self.verify_dragged_references(Path(prim_path).stem, prim_path, get_prims(stage, stage_prims))
