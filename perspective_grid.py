#!/usr/bin/python

import math
from gimpfu import *

class Thing(object):
  def __init__(self, d):
    for k, v in d.items():
      setattr(self, k, v)

def _hypotenuse(dx, dy):
  return math.sqrt(dx*dx + dy*dy)

def _long_enough_radius(ctx):
  '''Length for perspective-lines which should always reach across canvas'''
  dx = max(abs(ctx.x0), abs(ctx.x1-ctx.ll.width))
  dy = max(-ctx.hor_y, ctx.hor_y-ctx.ll.height)
  dc = _hypotenuse(dx, dy) # distance from vp to canvas
  diag = _hypotenuse(ctx.ll.width, ctx.ll.height)
  return int(dc + diag)

def _handle_vp(ctx, vpx, nlines, color):
  a0 = 0 if vpx > ctx.ll.width/2 else math.pi
  r = _long_enough_radius(ctx)
  angs = [a0 + math.pi * (0.5 + float(i)/nlines) for i in range(nlines)]
  points = [(vpx + r * math.cos(a), ctx.hor_y + r * math.sin(a)) for a in angs]
  pdb.gimp_context_set_foreground(color)
  for x, y in points:
    pdb.gimp_paintbrush_default(ctx.ll, 4, [vpx, ctx.hor_y, x, y])


# tdrawable is current layer

def entry_point(timg, tdrawable, n0, x0, color0, n1, x1, color1, hor_y, output_layer):
  ctx = Thing(locals())
  pdb.gimp_image_undo_group_start(timg)

  ctx.ll = gimp.Layer(timg, output_layer, tdrawable.width, tdrawable.height, RGBA_IMAGE, 100,
      NORMAL_MODE)
  timg.add_layer(ctx.ll)
  _handle_vp(ctx, x0, n0, color0)
  _handle_vp(ctx, x1, n1, color1)


  pdb.gimp_image_undo_group_end(timg)

register(
        "python_fu_perspective_grid",
        "Perspective grid plugin",
        "Perspective grid plugin",
        "AsherBlum",
        "AsherBlum",
        "2015",
        "<Image>/Tools/Perspective/Grid...",
        "RGB*, GRAY*",
        [
                (PF_INT, "n0", "# lines from left vp", 50),
                (PF_INT, "x0", "Left vanishing point x", -200),
                (PF_COLOR, "color0", "Color for left vanishing point", (0,255,0)),
                (PF_INT, "n1", "# lines from right vp", 50),
                (PF_INT, "x1", "Right vanishing point x", 1000),
                (PF_COLOR, "color1", "Color for right vanishing point", (255,0,0)),
                (PF_INT, "hor_y", "Horizon height", 1000),
                (PF_STRING, "output_layer", "New output layer", "perspective-grid"),
        ],
        [],
        entry_point)

main()
