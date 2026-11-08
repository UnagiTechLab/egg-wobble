# Maya: EggWobble — procedural wobbly disc (egg-white outline + yolk).
# Version: 1.2.1
#
# Copyright (c) 2026 Unagi Tech Inc.
# Credit: This script was created by Unagi Tech Inc.
#
# License: MIT (see LICENSE). Keep this credit when you modify or redistribute.
#   Provided as-is without warranty; not affiliated with Autodesk.
#
# What it does:
#   Polar Fourier blob: r(θ) = R * (1 + wobble * Σ amp_k cos(kθ + φ_k))
#   Low frequencies only (k=2,3,4) so the rim stays a soft egg-like blob.
#   Create → live slider preview → Confirm to bake a fixed result.
#
# Install (once): copy this file into Maya's user "scripts" folder (flat).
#   Windows:  Documents\maya\scripts\
#
# Script Editor — Python tab:
# import egg_wobble as ew
# ew.show()
# # after update: import importlib; importlib.reload(ew)

from __future__ import annotations

import math
from typing import Optional

import maya.api.OpenMaya as om
import maya.cmds as cmds

__version__ = "1.2.1"
TOOL_NAME = "EggWobble"

UI_NAME = "eggWobbleUI"
RESULT_GROUP = "ew_result"
LIVE_GROUP = "ew_live"

# Mesh-only: lift yolk a hair on +Y so it doesn't z-fight the white.
# Curves stay coplanar (Y=0).
YOLK_MESH_LIFT = 0.05

AMP2 = 0.35
AMP3 = 0.55
AMP4 = 0.25

# "mesh" | "curve" | None — what the live group currently represents.
_live_kind: Optional[str] = None


def _unique(name: str) -> str:
    if not cmds.objExists(name):
        return name
    i = 1
    while cmds.objExists(f"{name}_{i}"):
        i += 1
    return f"{name}_{i}"


def phases_from_seed(seed: int) -> tuple[float, float, float]:
    s = float(seed)
    return (
        0.31 + s * 0.73,
        1.17 + s * 1.19,
        2.04 + s * 0.47,
    )


def blob_radius(theta: float, radius: float, wobble: float, seed: int) -> float:
    p2, p3, p4 = phases_from_seed(seed)
    n = (
        AMP2 * math.cos(2.0 * theta + p2)
        + AMP3 * math.cos(3.0 * theta + p3)
        + AMP4 * math.cos(4.0 * theta + p4)
    )
    return radius * (1.0 + wobble * n)


def blob_ring(
    n: int,
    radius: float,
    wobble: float,
    seed: int,
    cx: float = 0.0,
    cz: float = 0.0,
) -> list[tuple[float, float, float]]:
    pts: list[tuple[float, float, float]] = []
    for i in range(n):
        theta = (2.0 * math.pi * i) / n
        r = blob_radius(theta, radius, wobble, seed)
        pts.append((cx + r * math.cos(theta), 0.0, cz + r * math.sin(theta)))
    return pts


def _create_fan_mesh(
    name: str,
    ring: list[tuple[float, float, float]],
    center: tuple[float, float, float],
) -> str:
    """Filled disc: center vertex + triangle fan. Winding so normals face +Y."""
    n = len(ring)
    verts = [om.MPoint(*center)] + [om.MPoint(*p) for p in ring]
    counts = [3] * n
    connects: list[int] = []
    for i in range(n):
        a = i + 1
        b = 1 + ((i + 1) % n)
        connects.extend([0, b, a])

    # Create transform first and pass as parent — avoids renaming "world"
    # when MFnMesh.create returns a shape whose parent lookup is ambiguous.
    xform = cmds.createNode("transform", name=name)
    sel = om.MSelectionList()
    sel.add(xform)
    parent_obj = sel.getDependNode(0)
    fn = om.MFnMesh()
    fn.create(verts, counts, connects, parent=parent_obj)
    cmds.polySoftEdge(xform, angle=180, constructionHistory=False)
    cmds.delete(xform, constructionHistory=True)
    return xform


def _ensure_lambert(shader_name: str, rgb: tuple[float, float, float]) -> str:
    sg = f"{shader_name}SG"
    if not cmds.objExists(shader_name):
        sh = cmds.shadingNode("lambert", asShader=True, name=shader_name)
        cmds.setAttr(f"{sh}.color", rgb[0], rgb[1], rgb[2], type="double3")
    else:
        sh = shader_name
    if not cmds.objExists(sg):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
        cmds.connectAttr(f"{sh}.outColor", f"{sg}.surfaceShader", force=True)
    return sg


def _assign(mesh: str, sg: str) -> None:
    cmds.sets(mesh, edit=True, forceElement=sg)


def _clear_live_group() -> None:
    global _live_kind
    if cmds.objExists(LIVE_GROUP):
        cmds.delete(LIVE_GROUP)
    _live_kind = None


def create_curve(
    *,
    seed: int = 7,
    white_radius: float = 5.0,
    wobble: float = 0.22,
    subdivs: int = 64,
    yolk_radius: float = 1.9,
    yolk_ox: float = -0.5,
    yolk_oz: float = 0.6,
    include_yolk: bool = True,
    group_name: Optional[str] = None,
) -> str:
    if group_name:
        if cmds.objExists(group_name):
            cmds.delete(group_name)
        grp = cmds.group(empty=True, name=group_name)
    else:
        grp = cmds.group(empty=True, name=_unique(RESULT_GROUP))

    ring = blob_ring(subdivs, white_radius, wobble, seed)
    n = len(ring)
    degree = 3
    # Periodic cubic: wrap first `degree` CVs. Knot length = #CVs + degree - 1.
    cvs = ring + ring[:degree]
    knots = list(range(-(degree - 1), n + degree))
    white = cmds.curve(
        degree=degree,
        periodic=True,
        point=cvs,
        knot=knots,
        name=_unique("ew_whiteCrv"),
    )
    cmds.parent(white, grp)

    if include_yolk:
        yolk = cmds.circle(
            name=_unique("ew_yolkCrv"),
            radius=yolk_radius,
            normal=(0, 1, 0),
            constructionHistory=False,
        )[0]
        cmds.setAttr(f"{yolk}.translateX", yolk_ox)
        cmds.setAttr(f"{yolk}.translateZ", yolk_oz)
        cmds.parent(yolk, grp)

    cmds.select(grp)
    return grp


def create_mesh(
    *,
    seed: int = 7,
    white_radius: float = 5.0,
    wobble: float = 0.22,
    subdivs: int = 64,
    yolk_radius: float = 1.9,
    yolk_ox: float = -0.5,
    yolk_oz: float = 0.6,
    thickness: float = 0.0,
    include_yolk: bool = True,
    assign_color: bool = True,
    group_name: Optional[str] = None,
) -> str:
    subdivs = max(12, int(subdivs))
    if group_name:
        if cmds.objExists(group_name):
            cmds.delete(group_name)
        grp = cmds.group(empty=True, name=group_name)
    else:
        grp = cmds.group(empty=True, name=_unique(RESULT_GROUP))

    ring = blob_ring(subdivs, white_radius, wobble, seed)
    white = _create_fan_mesh(_unique("ew_white"), ring, (0.0, 0.0, 0.0))
    cmds.parent(white, grp)

    yolk: Optional[str] = None
    if include_yolk:
        yolk_n = max(16, subdivs // 2)
        yolk_ring = []
        for i in range(yolk_n):
            t = (2.0 * math.pi * i) / yolk_n
            yolk_ring.append(
                (
                    yolk_ox + yolk_radius * math.cos(t),
                    0.0,
                    yolk_oz + yolk_radius * math.sin(t),
                )
            )
        yolk = _create_fan_mesh(
            _unique("ew_yolk"),
            yolk_ring,
            (yolk_ox, 0.0, yolk_oz),
        )
        cmds.parent(yolk, grp)

    if thickness > 1e-6:
        # Extrude white only; yolk stays a flat disc sitting just above the top.
        cmds.polyExtrudeFacet(
            f"{white}.f[*]",
            keepFacesTogether=True,
            localTranslateZ=thickness,
            constructionHistory=False,
        )
        cmds.delete(white, constructionHistory=True)

    if yolk:
        # Flat: tiny lift. Thick white: sit on top face + tiny lift.
        lift = (float(thickness) if thickness > 1e-6 else 0.0) + YOLK_MESH_LIFT
        cmds.setAttr(f"{yolk}.translateY", lift)

    if assign_color:
        white_sg = _ensure_lambert("ew_white_mtl", (1.0, 1.0, 1.0))
        _assign(white, white_sg)
        if yolk:
            yolk_sg = _ensure_lambert("ew_yolk_mtl", (1.0, 0.8, 0.0))
            _assign(yolk, yolk_sg)

    cmds.select(grp)
    return grp


# ---------------------------------------------------------------------------
# UI — live preview + confirm
# ---------------------------------------------------------------------------

def _q(ctrl: str):
    return cmds.intSliderGrp(ctrl, query=True, value=True)


def _qf(ctrl: str) -> float:
    return cmds.floatSliderGrp(ctrl, query=True, value=True)


def _params_from_ui() -> dict:
    return {
        "seed": int(_q("ew_seed")),
        "white_radius": _qf("ew_whiteR"),
        "wobble": _qf("ew_wobble"),
        "subdivs": int(_q("ew_subdivs")),
        "yolk_radius": _qf("ew_yolkR"),
        "yolk_ox": _qf("ew_yolkX"),
        "yolk_oz": _qf("ew_yolkZ"),
        "thickness": _qf("ew_thick"),
        "include_yolk": bool(cmds.checkBox("ew_yolkOn", query=True, value=True)),
        "assign_color": True,
    }


def _set_status(msg: str) -> None:
    if cmds.text("ew_status", exists=True):
        cmds.text("ew_status", edit=True, label=msg)


def _refresh_live(*, use_undo: bool = False) -> None:
    """Rebuild ew_live from current UI. No-op if nothing is in live session."""
    global _live_kind
    if _live_kind not in ("mesh", "curve"):
        return
    if not cmds.window(UI_NAME, exists=True):
        return

    def _build() -> None:
        p = _params_from_ui()
        if _live_kind == "mesh":
            create_mesh(**p, group_name=LIVE_GROUP)
        else:
            p.pop("thickness", None)
            p.pop("assign_color", None)
            create_curve(**p, group_name=LIVE_GROUP)
        _set_status(f"Live ({_live_kind}) — tweak sliders, then Confirm.")

    if use_undo:
        cmds.undoInfo(openChunk=True, chunkName="eggWobbleLive")
        try:
            _build()
        finally:
            cmds.undoInfo(closeChunk=True)
    else:
        # Slider drag: skip undo flood.
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            _build()
        finally:
            cmds.undoInfo(stateWithoutFlush=True)


def _start_live(kind: str) -> None:
    global _live_kind
    _live_kind = kind
    _refresh_live(use_undo=True)


def _on_live_param(*_args) -> None:
    if _live_kind in ("mesh", "curve"):
        _refresh_live(use_undo=False)


def _on_mesh(*_args) -> None:
    _start_live("mesh")


def _on_curve(*_args) -> None:
    _start_live("curve")


def _on_confirm(*_args) -> None:
    global _live_kind
    if _live_kind not in ("mesh", "curve") or not cmds.objExists(LIVE_GROUP):
        _set_status("Nothing to confirm — Create Mesh / Curve first.")
        return
    cmds.undoInfo(openChunk=True, chunkName="eggWobbleConfirm")
    try:
        baked = cmds.rename(LIVE_GROUP, _unique(RESULT_GROUP))
        _live_kind = None
        cmds.select(baked)
        _set_status(f"Confirmed → {baked}")
    finally:
        cmds.undoInfo(closeChunk=True)


def _on_discard(*_args) -> None:
    if _live_kind is None and not cmds.objExists(LIVE_GROUP):
        _set_status("No live preview.")
        return
    cmds.undoInfo(openChunk=True, chunkName="eggWobbleDiscard")
    try:
        _clear_live_group()
        _set_status("Live preview discarded.")
    finally:
        cmds.undoInfo(closeChunk=True)


def _on_random(*_args) -> None:
    import random

    cmds.intSliderGrp("ew_seed", edit=True, value=random.randint(0, 9999))
    if _live_kind in ("mesh", "curve"):
        _refresh_live(use_undo=True)
    else:
        _start_live("mesh")


def _on_reset_defaults(*_args) -> None:
    """Restore UI to factory defaults (same as show() initial values)."""
    cmds.intSliderGrp("ew_seed", edit=True, value=7)
    cmds.floatSliderGrp("ew_whiteR", edit=True, value=5.0)
    cmds.floatSliderGrp("ew_wobble", edit=True, value=0.22)
    cmds.intSliderGrp("ew_subdivs", edit=True, value=64)
    cmds.checkBox("ew_yolkOn", edit=True, value=True)
    cmds.floatSliderGrp("ew_yolkR", edit=True, value=1.9)
    cmds.floatSliderGrp("ew_yolkX", edit=True, value=-0.5)
    cmds.floatSliderGrp("ew_yolkZ", edit=True, value=0.6)
    cmds.floatSliderGrp("ew_thick", edit=True, value=0.0)
    if _live_kind in ("mesh", "curve"):
        _refresh_live(use_undo=True)
        _set_status(f"Defaults restored — live ({_live_kind}) updated.")
    else:
        _set_status("Defaults restored.")


def _wire_slider(ctrl: str, is_int: bool = False) -> None:
    if is_int:
        cmds.intSliderGrp(
            ctrl,
            edit=True,
            changeCommand=_on_live_param,
            dragCommand=_on_live_param,
        )
    else:
        cmds.floatSliderGrp(
            ctrl,
            edit=True,
            changeCommand=_on_live_param,
            dragCommand=_on_live_param,
        )


def show() -> None:
    global _live_kind
    if cmds.window(UI_NAME, exists=True):
        cmds.deleteUI(UI_NAME)
    # Former UI id (pre-EggWobble rename).
    if cmds.window("friedEggBlobUI", exists=True):
        cmds.deleteUI("friedEggBlobUI")
    # Migrate former live group name if present.
    if cmds.objExists("feb_live") and not cmds.objExists(LIVE_GROUP):
        cmds.rename("feb_live", LIVE_GROUP)
    # Keep an existing ew_live in the scene; reattach if present.
    if cmds.objExists(LIVE_GROUP):
        if _live_kind not in ("mesh", "curve"):
            _live_kind = "mesh"
    else:
        _live_kind = None

    win = cmds.window(
        UI_NAME,
        title=f"{TOOL_NAME} v{__version__}",
        widthHeight=(440, 480),
        sizeable=True,
    )
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnAttach=("both", 8))
    cmds.text(
        label="Create → live sliders → Confirm to bake. XZ plane, +Y up.",
        align="left",
    )
    cmds.intSliderGrp(
        "ew_seed",
        label="Seed",
        field=True,
        minValue=0,
        maxValue=9999,
        value=7,
        step=1,
    )
    cmds.floatSliderGrp(
        "ew_whiteR",
        label="White radius",
        field=True,
        minValue=0.1,
        maxValue=50.0,
        value=5.0,
        precision=3,
    )
    cmds.floatSliderGrp(
        "ew_wobble",
        label="Wobble",
        field=True,
        minValue=0.0,
        maxValue=0.55,
        value=0.22,
        precision=3,
    )
    cmds.intSliderGrp(
        "ew_subdivs",
        label="Subdivs",
        field=True,
        minValue=16,
        maxValue=256,
        value=64,
        step=1,
    )
    cmds.checkBox(
        "ew_yolkOn",
        label="Include yolk",
        value=True,
        changeCommand=_on_live_param,
    )
    cmds.floatSliderGrp(
        "ew_yolkR",
        label="Yolk radius",
        field=True,
        minValue=0.05,
        maxValue=20.0,
        value=1.9,
        precision=3,
    )
    cmds.floatSliderGrp(
        "ew_yolkX",
        label="Yolk offset X",
        field=True,
        minValue=-10.0,
        maxValue=10.0,
        value=-0.5,
        precision=3,
    )
    cmds.floatSliderGrp(
        "ew_yolkZ",
        label="Yolk offset Z",
        field=True,
        minValue=-10.0,
        maxValue=10.0,
        value=0.6,
        precision=3,
    )
    cmds.floatSliderGrp(
        "ew_thick",
        label="Thickness (0=flat)",
        field=True,
        minValue=0.0,
        maxValue=10.0,
        value=0.0,
        precision=3,
    )

    for c in ("ew_seed", "ew_subdivs"):
        _wire_slider(c, is_int=True)
    for c in (
        "ew_whiteR",
        "ew_wobble",
        "ew_yolkR",
        "ew_yolkX",
        "ew_yolkZ",
        "ew_thick",
    ):
        _wire_slider(c, is_int=False)

    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3, columnWidth3=(130, 130, 130))
    cmds.button(label="Create Mesh", height=32, command=_on_mesh)
    cmds.button(label="Create Curve", height=32, command=_on_curve)
    cmds.button(label="Randomize", height=32, command=_on_random)
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3, columnWidth3=(145, 145, 145))
    cmds.button(
        label="Confirm（確定）",
        height=36,
        backgroundColor=(0.35, 0.55, 0.35),
        command=_on_confirm,
    )
    cmds.button(label="Discard live", height=36, command=_on_discard)
    cmds.button(label="Reset defaults", height=36, command=_on_reset_defaults)
    cmds.setParent("..")
    cmds.text(
        "ew_status",
        label="Ready — Create Mesh / Curve to start live preview.",
        align="left",
        font="smallPlainLabelFont",
    )
    cmds.text(
        label="Seed 7 + wobble 0.22 matches the sample SVG look.",
        align="left",
        font="smallPlainLabelFont",
    )
    cmds.showWindow(win)
