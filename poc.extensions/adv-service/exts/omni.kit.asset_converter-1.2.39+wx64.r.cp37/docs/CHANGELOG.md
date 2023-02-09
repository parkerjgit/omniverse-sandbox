# Changelog

## [1.2.39] - 2022-10-26
### Changed
- Update OmniverseAssetConverter library to 7.0.1303 to fix uv export of FBX when there are multi-subsets.

## [1.2.38] - 2022-10-11
### Changed
- Update OmniverseAssetConverter library to 7.0.1301 to avoid export fallback color for obj import.

## [1.2.37] - 2022-10-07
### Changed
- Update OmniverseAssetConverter library to 7.0.1300 to fix path resolve issue under linux when it's to reference glTF directly.

## [1.2.36] - 2022-09-08
### Changed
- Add support for BVH file imports.
- Update OmniverseAssetConverter library to 7.0.1293.

## [1.2.35] - 2022-09-03
### Changed
- Update tests to pass for kit 104.

## [1.2.34] - 2022-09-01
### Changed
- Update OmniverseAssetConverter library to 7.0.1289.
- Fix export crash caused by invalid normal data from usd.
- Merge skeletons for glTF to have single skeleton.

## [1.2.33] - 2022-08-05
### Changed
- Update OmniverseAssetConverter library to 7.0.1286.
- Fix issue of material naming conflict during USD export.
- Export kind for root node during USD export.
- Fix crash of exporting USD into OBJ caused by mal-formed USD data.

## [1.2.32] - 2022-07-22
### Changed
- Update OmniverseAssetConverter library to 7.0.1270.
- Fix hang of USD plugin to reference glTF from server.
- Improve glTF light import/export.

## [1.2.31] - 2022-06-07
### Changed
- Update OmniverseAssetConverter library to 7.0.1258.
- OM-52881: Fix some glb file cause crashs in importer.

## [1.2.30] - 2022-05-19
### Changed
- Update OmniverseAssetConverter library to 7.0.1253.
- OM-51000: support to pass file argument for specifying meter as world unit.
- Improve file format plugin to import asset with original units instead of baking scalings.

## [1.2.29] - 2022-05-19
### Changed
- Update OmniverseAssetConverter library to 7.0.1250 to fix issue of converting assets to local path under linux.

## [1.2.28] - 2022-05-16
### Changed
- Update OmniverseAssetConverter library to 7.0.1245
- OM-50555: Fix fbx animation rotation
- OM-50991: optimize uv export to fix texture load not properly

## [1.2.27] - 2022-05-12
### Changed
- Update OmniverseAssetConverter library to 7.0.1237 to fix pdb name issue for assimp library.

## [1.2.26] - 2022-05-07
### Changed
- Fix tests to make sure it will not fail for 103.1 release.

## [1.2.25] - 2022-05-04
### Changed
- Update OmniverseAssetConverter library to 7.0.1236.
- OM-36894: Support fbx uv indices's import and export.
- OM-34328: Support export lights for gltf.

## [1.2.24] - 2022-04-19
### Changed
- Update OmniverseAssetConverter library to 7.0.1225.
- Fix naming issue of obj import if mesh names are empty.
- Fix color space setup for material loader.
- Fix geometric transform import for FBX.

## [1.2.23] - 2022-04-12
### Changed
- Update OmniverseAssetConverter library to 7.0.1219 to support dissovle attribute of MTL for obj importer.

## [1.2.22] - 2022-03-30
### Changed
- Bump version to update licensing build.

## [1.2.21] - 2022-03-29
### Changed
- Supports option to close current stage with import to avoid multi-threading issue if output path is opened already.

## [1.2.20] - 2022-03-28
### Changed
- Update OmniverseAssetConverter library to 7.0.1201 to support option to bake scales for FBX import.

## [1.2.19] - 2022-03-09
### Changed
- Update OmniverseAssetConverter library to 7.0.1197 to improve pivots support for exporter.
- Fix issue that exports USD with pivots to gltf/obj.

## [1.2.18] - 2022-03-08
### Changed
- Update OmniverseAssetConverter library to 7.0.1192 to support to control hidden props export for USD exporter.

## [1.2.17] - 2022-03-04
### Changed
- Update OmniverseAssetConverter library to 7.0.1191 to improve animation import for FBX.
- Fix issue of skeletal mesh import when skeleton is not attached to root node.
- Fix issue of skeletal mesh if its joints is not provided, which should use global joints instead.
- Fix crash of skeleton import if skeleton removed and skinning is still existed.
- Fix issue of FBX importer that has possible naming conflict of nodes.
- Supports to export all instances into single USD for DriveSim usecase.
- Supports options to disable scene instancing for DriveSim usecase.

## [1.2.16] - 2022-02-22
### Changed
- Update OmniverseAssetConverter library to 7.0.1171 to improve multiple animation tracks import/export.

## [1.2.15] - 2022-02-16
### Changed
- Update OmniverseAssetConverter library to 7.0.1161 to remove instancing flag if glTF/glb is opened directly with file format plugin so it could be editable.

## [1.2.14] - 2022-02-15
### Changed
- Update OmniverseAssetConverter library to 7.0.1159 to fix a crash of fbx importer that accesses invalid attributes.

## [1.2.13] - 2022-02-15
### Changed
- Update OmniverseAssetConverter library to 7.0.1157 to improve glTF loading performance through file format plugin.

## [1.2.12] - 2022-02-13
### Changed
- Update OmniverseAssetConverter library to 7.0.1150 to fix a FBX exporter crash that's caused by empty uv set.

## [1.2.11] - 2022-02-11
### Changed
- Update OmniverseAssetConverter library to 7.0.1149 to fix a FBX exporter issue that ignores props under root node.

## [1.2.10] - 2022-02-11
### Changed
- Fix API docs.

## [1.2.9] - 2022-02-10
### Changed
- Update OmniverseAssetConverter library to 7.0.1148 to fix a crash caused by exporting obj files without materials.

## [1.2.8] - 2022-02-08
### Changed
- Update OmniverseAssetConverter library to 7.0.1145 to fix a crash that's caused by invalid path that includes "%" symbols.

## [1.2.7] - 2022-02-07
### Changed
- Update OmniverseAssetConverter library to 7.0.1143 to improve USD exporter to exclude proxy and guide prims.

## [1.2.6] - 2022-02-07
### Changed
- Update OmniverseAssetConverter library to 7.0.1142 to fix glTF import.
- Uses default mime type based on extension name if it's not specified for textures.
- Fix transparent material import.

## [1.2.5] - 2022-01-11
### Changed
- Update OmniverseAssetConverter library to 7.0.1138 to fix a regression to import assets to OV.

## [1.2.4] - 2022-01-09
### Changed
- Update OmniverseAssetConverter library to 7.0.1136.
- Re-org skeletal animation.
- Fix transform issue of obj export.
- Improve export for FBX assets exported from Substance Painter to avoid exporting separate parts for the same mesh.

## [1.2.3] - 2021-12-30
### Changed
- Update OmniverseAssetConverter library to 7.0.1127 to export obj model as meshes instead of group of subsets so subsets can be pickable.

## [1.2.2] - 2021-12-29
### Changed
- Update OmniverseAssetConverter library to 7.0.1123 to use tinyobj for obj import.

## [1.2.1] - 2021-12-23
### Changed
- Update OmniverseAssetConverter library to 7.0.1117 to support override file copy to speed up copying file.
- More optimization to avoid redundant IO to speed up glTF import.

## [1.2.0] - 2021-12-16
### Changed
- Update OmniverseAssetConverter library to 7.0.1115 to improve exporter.
- Replace assimp with tinygltf for glTF import/export.
- Refactoring stage structure to improve animation export.
- Refactoring stage structure to support scene instancing.
- Lots of improvement and bugfixes.

## [1.1.43] - 2021-12-01
### Changed
- Update OmniverseAssetConverter library to 7.0.1061 to rotation order issue of FBX import.
- Add option to control pivots generation.
- Use euler angles for rotation by default for FBX import.

## [1.1.42] - 2021-10-09
### Changed
- Update OmniverseAssetConverter library to 7.0.1041 to fix memory leak, and improve uv set import.

## [1.1.41] - 2021-10-08
### Changed
- Update OmniverseAssetConverter library to 7.0.1040 to fix opacity map export issue of FBX importer.

## [1.1.40] - 2021-10-06
### Changed
- Update OmniverseAssetConverter library to 7.0.1039 to improve exporter.

## [1.1.39] - 2021-09-30
### Changed
- Update initialization order to make sure format plugin loaded correctly.

## [1.1.38] - 2021-09-23
### Changed
- Update OmniverseAssetConverter library to 7.0.1024 to fix color space import of textures.

## [1.1.37] - 2021-09-22
### Changed
- Update OmniverseAssetConverter library to 7.0.1020 to improve exporter.
- Supports to import/export glTF from/to UsdPreviewSurface and glTF MDL.
- Supports to export USDZ to glTF.

## [1.1.36] - 2021-09-12
### Changed
- Update OmniverseAssetConverter library to 7.0.1012 to integrate latest glTF MDL to support transmission/sheen/texture transform extensions.

## [1.1.35] - 2021-09-07
### Changed
- Update OmniverseAssetConverter library to 7.0.1007 to use translate/orient/scale for transform to fix interpolation issues of animation samples of assimp importer.
- Fix camera import of assimp importer.
- Improve and fix rigid/skeletal animation import for glTF.

## [1.1.34] - 2021-09-03
### Changed
- Update OmniverseAssetConverter library to 7.0.1002 to fix crash caused by invalid memory access.

## [1.1.33] - 2021-09-03
### Changed
- Update OmniverseAssetConverter library to 7.0.999 to improve glTF import.
- Fix material naming conflict for glTF import for USD exporter.
- Fix tuple property set for material loader.

## [1.1.32] - 2021-09-01
### Changed
- Update OmniverseAssetConverter library to 7.0.989 to reduce artifacts size for linux.

## [1.1.31] - 2021-09-01
### Changed
- Update OmniverseAssetConverter library to 7.0.988 to fix linux build caused by DRACO symbol conflict between assimp and USD.

## [1.1.30] - 2021-08-30
### Changed
- Update OmniverseAssetConverter library to 7.0.984 to support import material as UsdPreviewSurface.
- Enable support to import draco compressed meshes of glTF.

## [1.1.29] - 2021-08-09
### Changed
- Update OmniverseAssetConverter library to 7.0.962 to support export non-skinned skeleton.

## [1.1.28] - 2021-08-05
### Changed
- Update OmniverseAssetConverter library to 7.0.961 to fix camera animation issue.

## [1.1.27] - 2021-07-27
### Changed
- Update OmniverseAssetConverter library to 7.0.956 to check invalid mesh to avoid crash.

## [1.1.26] - 2021-07-22
### Changed
- Update AssetConverterContext to support a to_dict() function.

## [1.1.25] - 2021-07-10
### Changed
- Update OmniverseAssetConverter library to 7.0.950 for better glTF material import support.

## [1.1.24] - 2021-06-09
### Fixes
- Use copy on overwrite to avoid removing file firstly for files upload.

## [1.1.23] - 2021-06-07
### Changed
- Update OmniverseAssetConverter library to 7.0.943 to fix default prim issue of animation clip import.

## [1.1.22] - 2021-06-02
### Changed
- Add param for converter context to customize precision of USD transform op.

## [1.1.21] - 2021-06-02
### Changed
- Update OmniverseAssetConverter library to 7.0.942 for supporting customizing precision of USD transform op.

## [1.1.20] - 2021-05-25
### Changed
- Update OmniverseAssetConverter library to 7.0.941 for more glTF import improvement.

## [1.1.19] - 2021-05-10
### Changed
- Update OmniverseAssetConverter library to 7.0.933 to support pivot.

## [1.1.18] - 2021-05-07
### Changed
- Update OmniverseAssetConverter library to 7.0.928 to fix and improve glTF export.
- Add glb import/export support.
- Add embedding textures support for glTF/glb export support.

## [1.1.17] - 2021-05-06
### Changed
- Update OmniverseAssetConverter library to 7.0.925 to fix and improve glTF import.
- Shorten library search path to mitigate long path issue.
### Fixes
- Fix camera import and export issue.
- Fix OmniPBR material export issue for FBX.

## [1.1.16] - 2021-05-05
### Changed
- Update assimp to latest.
### Fixes
- Fix crash to import cameras from glTF.

## [1.1.15] - 2021-05-04
### Changed
- Update OmniverseAssetConverter library to 7.0.916 to provide WA for supporting pivots from FBX files.

## [1.1.14] - 2021-04-28
### Changed
- Update OmniverseAssetConverter library to 7.0.914 to include float type support and fix default/min/max issue of material loader.

## [1.1.13] - 2021-04-12
### Fixes
- Fix the crash to import FBX file that's over 2GB.

## [1.1.12] - 2021-03-30
### Changed
- Update extension icon.
- Remove extension warning.

## [1.1.11] - 2021-03-29
### Changed
- Support to merge all static meshes if they are under the same transform and no skin meshes are there.

## [1.1.10] - 2021-03-24
### Fixes 
- Fix anonymous USD export.
- Fix crash of empty stage export to OBJ.

## [1.1.9] - 2021-03-24
### Fixes 
- Fix texture populates for FBX that's referenced by property of texture object.

## [1.1.8] - 2021-03-23
### Changed
- Improve material export to display all material params for Kit editing.

## [1.1.7] - 2021-03-19
### Changed
- Shorten the length of native library path to avoid long path issue.

## [1.1.6] - 2021-03-06
### Changed
- Improve texture uploading to avoid those that are not referenced.

## [1.1.5] - 2021-03-05
### Changed
- Support to remove redundant materials that are not referenced by any meshes.

## [1.1.4] - 2021-02-20
### Fixes
- Fix issue that exports timesamples when it has no real transform animation.

## [1.1.3] - 2021-02-19
### Fixes
- More fixes to long path issue on windows.

## [1.1.2] - 2021-02-18
### Fixes
- Shorten the path length of native libraries to fix long path issue.

## [1.1.1] - 2021-02-16
### Fixes
- Fix obj export crash when there are no materials.

## [1.1.0] - 2021-02-15
### Changed
- Separate asset converter from Kit as standalone repo.

## [1.0.1] - 2021-01-26
### Changed
- Add animation export for FBX export.
- Add options to support embedding textures for FBX export

### Fixes
- Fix opacity map import/export for fbx.
- Animation import fixes.
  
## [1.0.0] - 2021-01-19
### Changed 
- Initial extension from original omni.kit.tool.asset_importer.
