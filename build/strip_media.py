"""Run after data/ is copied into dist/: re-save every published image without EXIF (GPS, camera) and cap its width."""
import os, sys
from PIL import Image, ImageOps
root = sys.argv[1] if len(sys.argv) > 1 else '../dist/data/media'
for dp, _, fs in os.walk(root):
    for f in fs:
        ext = f.lower().rsplit('.', 1)[-1]
        if ext not in ('jpg', 'jpeg', 'png', 'webp'): continue
        p = os.path.join(dp, f)
        try:
            im = ImageOps.exif_transpose(Image.open(p))
            if im.size[0] > 1600: im = im.resize((1600, round(im.size[1] * 1600 / im.size[0])), Image.LANCZOS)
            if ext in ('jpg', 'jpeg'): im.convert('RGB').save(p, 'JPEG', quality=85, optimize=True)
            elif ext == 'png': im.save(p, 'PNG', optimize=True)
            else: im.save(p, 'WEBP', quality=85)
            print('cleaned', f, os.path.getsize(p) // 1024, 'KB')
        except Exception as ex:
            print('WARNING: could not clean', f, ex)
