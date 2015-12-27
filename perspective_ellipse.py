#!/usr/bin/python

import copy
import math
from gimpfu import *

class Thing(object):
  def __init__(self, d):
    for k, v in d.items():
      setattr(self, k, v)

def _is_rect(stroke):
  points, _ = stroke.points
  if len(points) != 24:
    return False
  # further check would be good here: internal redundancy ...
  return True

def _stroke_to_bbox(stroke):
  points, _ = stroke.points
  xx = [points[i] for i in [0, 6, 12, 18]]
  yy = [points[i] for i in [1, 7, 13, 19]]
  return (min(xx), min(yy), max(xx), max(yy))

def _rect_to_toplines(spacing, stroke):
  '''Stroke -> (x0, x1, y)'''
  x0, y0, x1, y1 = _stroke_to_bbox(stroke)
  dy = y1 - y0
  dx = x1 - x0

  # wide, short rectangle -> one ellipse
  if dy < 2 * spacing:
    return [(x0, x1, y0)]

  # tall skinny rectangle -> stack of ellipses
  res = []
  y = y0
  while y < y1:
    res.append((x0, x1, y))
    y += spacing
  res.append((x0, x1, y1))
  return res

def _rect_to_vlines(ctx, stroke):
  x0, y0, x1, y1 = _stroke_to_bbox(stroke)

  _, etop, _, _ = _compute_ellipse(ctx, (x0, x1, y0))
  _, ebot, _, bh =_compute_ellipse(ctx, (x0, x1, y1))

  y0 = etop
  y1 = ebot + bh

  da = abs(2.0 * math.pi / ctx.vl_qty)
  a = da * abs(float(ctx.vl_offset_pc))/100.0
  xc = (x0 + x1)/2.0
  rad = abs(x1-x0)/2.0
  res = []
  while a < 2.0 * math.pi:
    x = xc + rad * math.cos(a)
    opacity = ctx.vl_front_opacity
    if a > math.pi/4.0 and a < 0.75 * math.pi:
      opacity = ctx.vl_back_opacity
    res.append((x, y0, y1, opacity))
    a += da
  return res

def _draw_ellipse(ctx, opacity, x, y, w, h):
  if h < 2: # cannot draw 0-height ellipse
    return
  pdb.gimp_image_select_ellipse(ctx.timg, CHANNEL_OP_REPLACE, x, y, w, h)
  pdb.gimp_context_set_opacity(opacity)
  pdb.gimp_edit_stroke(ctx.ll)

def _erase_back_half(ctx, topline, height):
  x0, x1, y = topline
  width  = abs(x1 - x0)
  ellipse_top = y - int(height/2)
  ry = ellipse_top
  if y < ctx.hor_y: # above horizon
    ry += int(height/2) # gray out bottom half
  else:
    ry -= ctx.extra
  pdb.gimp_image_select_rectangle(ctx.timg, CHANNEL_OP_REPLACE, x0-ctx.extra, ry, int(width+2*ctx.extra), int(height/2 + ctx.extra))
  pdb.gimp_edit_clear(ctx.ll)

def _compute_ellipse(ctx, topline):
  img_top_height = float(ctx.hor_y) # top edge = 0, so ...
  x0, x1, y = topline
  width  = abs(x1 - x0)
  our_height = abs(float(y - ctx.hor_y))
  height_r = our_height / img_top_height
  height = ctx.max_ar * height_r * width
  ellipse_top = y - int(height/2)
  return (x0, ellipse_top, width, height)

def _handle_ellipse(ctx, topline):
  x0, ellipse_top, width, height = _compute_ellipse(ctx, topline)

  # paint at full opacity
  _draw_ellipse(ctx, 100,  x0, ellipse_top, int(width), int(height))

  # erase back half of ellipse:
  _erase_back_half(ctx, topline, height)

  # paint again at lower opacity
  _draw_ellipse(ctx, ctx.back_opacity,  x0, ellipse_top, int(width), int(height))

def _handle_vline(ctx, vline):
  x, y0, y1, opacity = vline
  pdb.gimp_context_set_opacity(opacity)
  pdb.gimp_paintbrush_default(ctx.ll, 4, [x,y0,x,y1])


  # tdrawable is current layer ...
def entry_point(timg, tdrawable, max_ar, hor_y, v_spacing, back_opacity, output_layer, vl_enable, vl_qty, vl_front_opacity, vl_back_opacity, vl_offset_pc):
  ctx = Thing(locals())
  pdb.gimp_image_undo_group_start(timg)

  ctx.extra = pdb.gimp_context_get_brush_size() + 1
  ctx.ll = gimp.Layer(timg, output_layer, tdrawable.width, tdrawable.height, RGBA_IMAGE, 100,
      NORMAL_MODE)
  timg.add_layer(ctx.ll)

  # selection -> path
  pdb.plug_in_sel2path(timg, None)

  # they may be rects ...
  rects = timg.vectors[0].strokes
  rects = [r for r in rects if _is_rect(r)]
  toplines = []
  vlines = []
  for r in rects:
    toplines.extend(_rect_to_toplines(v_spacing, r))
    vlines.extend(_rect_to_vlines(ctx, r))

  # rm our new path:
  pdb.gimp_image_remove_vectors(timg, timg.vectors[0])

  for topline in toplines:
    _handle_ellipse(ctx, topline)

  pdb.gimp_selection_all(timg)

  if ctx.vl_enable:
    for vline in vlines:
      _handle_vline(ctx, vline)

  pdb.gimp_image_undo_group_end(timg)

register(
        "python_fu_perspective_ellipse",
        "Perspective ellipse plugin",
        "Perspective ellipse plugin",
        "AsherBlum",
        "AsherBlum",
        "2015",
        "<Image>/Tools/Perspective/Ellipses...",
        "RGB*, GRAY*",
        [
                (PF_FLOAT, "max_ar", "Top aspect ratio", .25),
                (PF_INT, "hor_y", "Horizon height", 1000),
                (PF_INT, "v_spacing", "Vertical spacing", 100),
                (PF_FLOAT, "back_opacity", "Ellipse back opacity", 30.0),
                (PF_STRING, "output_layer", "New output layer", "ellipse"),
                (PF_BOOL, "vl_enable", "Draw vertical lines", False),
                (PF_INT, "vl_qty", "Number of vertical lines", 16),
                (PF_FLOAT, "vl_front_opacity", "Vertical line front opacity", 70.0),
                (PF_FLOAT, "vl_back_opacity", "Vertical line back opacity", 20.0),
                (PF_INT, "vl_offset_pc", "Vertical line offset angle percent", 25),
        ],
        [],
        entry_point)

main()
