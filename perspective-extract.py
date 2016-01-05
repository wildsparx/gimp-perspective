#!/usr/bin/python

import math
from gimpfu import *

GERR = "This plugin needs a path with four points."

class Thing(object):
  def __init__(self, d):
    for k, v in d.items():
      setattr(self, k, v)

def _hypotenuse(dx, dy):
  return math.sqrt(dx*dx + dy*dy)

def _long_enough_radius(ctx, vp):
  '''Length for perspective-lines which should always reach across canvas'''
  vpx, vpy = vp
  dx = max(abs(vpx), abs(vpx-ctx.ll.width))
  dy = max(-vpy, vpy-ctx.ll.height)
  dc = _hypotenuse(dx, dy) # distance from vp to canvas
  diag = _hypotenuse(ctx.ll.width, ctx.ll.height)
  return int(dc + diag)

def _handle_vp(ctx, vp, nlines, color):
  vpx, vpy = vp
  #a0 = 0 if vpx > ctx.ll.width/2 else math.pi
  a0 = 0
  r = _long_enough_radius(ctx, vp)
  angs = [2.0 * math.pi * float(i)/nlines for i in range(nlines)]
  points = [(vpx + r * math.cos(a), vpy + r * math.sin(a)) for a in angs]
  pdb.gimp_context_set_foreground(color)
  for x, y in points:
    pdb.gimp_paintbrush_default(ctx.ll, 4, [vpx, vpy, x, y])


def _shape_to_lines(stroke):
  points, _ = stroke.points
  #print "stox: len=%d  points=%r" % (len(points), points)
  if len(points) != 24:
    return None
  # take first pair of each 3 pairs:
  points = [(points[i], points[i+1]) for i in range(0, len(points), 6)]
  #print "stox: uniq points=%r" % points
  # now have 4
  if len(points) != 4:
    return False
  lines = [(points[i], points[(i+1)%4]) for i in range(4)]
  return lines

def _line_to_si(line):
  '''(x,y) -> (slope, intercept)'''
  p0, p1 = line
  dx = float(p1[0]) - p0[0]
  dy = float(p1[1]) - p0[1]
  if dx == 0.0:
    return None
  m = dy/dx
  b = float(p0[1]) - m * p0[0]
  return (m, b)

def _intersect(a, b):
  '''(m, b), (m, b) -> (x, y)'''
  m0, b0 = a
  m1, b1 = b
  x = (b1-b0)/(m0-m1)
  y = m0 * x + b0
  return (x, y)
  
def _normalize_line(l):
  '''Make line go left->right'''
  a, b = l
  if a[0] > b[0]:
    return l
  return (b, a)
  
def _reorder_lines(lines):
  md = []
  for i, a in enumerate(lines):
    for j, b in enumerate(lines):
      if a != b:
        md.append((abs(a[0]-b[0]), a, b))
  md.sort()
  olines = list(md[0][1:])
  remaining = set(lines) - set(olines)
  return olines + list(remaining)
  


def _draw_line(ctx, line):
  points = list(line[0]) + list(line[1])
  pdb.gimp_paintbrush_default(ctx.ll, 4, points)

# tdrawable is current layer

def entry_point(timg, tdrawable, n0, color0, layer_name0, n1, color1, layer_name1):
  ctx = Thing(locals())
  pdb.gimp_image_undo_group_start(timg)
  try:

    layers = [ gimp.Layer(timg, name, tdrawable.width, tdrawable.height, RGBA_IMAGE, 100,
        NORMAL_MODE) for name in [layer_name0, layer_name1]]
    timg.add_layer(layers[0])
    timg.add_layer(layers[1])

    # take user-defined path

    if len(timg.vectors) < 1:
      raise RuntimeError(GERR)

    shapes = timg.vectors[0].strokes
    lines = _shape_to_lines(shapes[0])

    if not lines:
      raise RuntimeError(GERR)

    lines = [_normalize_line(l) for l in lines]
    ctx.ll = layers[0]

    lines = [_line_to_si(l) for l in lines]
    lines = list(set(lines))
    lines = _reorder_lines(lines)
    #print "about to intersect: %r" % lines
    vps = [_intersect(lines[i], lines[i+1]) for i in [0, 2]]
    print "vps=%r" % vps
    ctx.ll = layers[0]
    _handle_vp(ctx, vps[0], n0, color0)
    ctx.ll = layers[1]
    _handle_vp(ctx, vps[1], n1, color1)
  finally:
    pdb.gimp_image_undo_group_end(timg)



register(
        "python_fu_perspective_extract",
        "Perspective / Extract Grid",
        "Perspective / Extract Grid",
        "AsherBlum",
        "AsherBlum",
        "2016",
        "<Image>/Tools/Perspective/Extract Grids...",
        "RGB*, GRAY*",
        [
                (PF_INT, "n0", "# lines from first vp", 50),
                (PF_COLOR, "color0", "Color for first vp", (0,255,0)),
                (PF_STRING, "layer_name0", "New output layer for first vp", "perspective1"),
                (PF_INT, "n1", "# lines from second vp", 50),
                (PF_COLOR, "color1", "Color for second vanishing point", (255,0,0)),
                (PF_STRING, "layer_name1", "New output layer for secon vp", "perspective2"),
        ],
        [],
        entry_point)

main()
