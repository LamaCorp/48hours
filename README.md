# 48 hours of code between two friends and a wonderful library

[![pipeline status](https://gitlab.com/lama-corp/48hours/badges/master/pipeline.svg)](https://gitlab.com/lama-corp/48hours/commits/master)

Let's see what can come out of it

## I wanna play!

To run it:
```bash
# Create a venv if you want to
git clone https://gitlab.com/lama-corp/48hours.git lama-destroys-the-world
cd lama-destroys-the-world
pip3 install -r requirements.txt
python .
# Have fun!
```

### Contributing

##### Creating maps

Level design is hard, and we're not obviously good at it. If you'd like to create maps (hopefully better than ours!),
feel free to do so, and submit them in a Merge Request.

To create maps, we have a wonderful level editor. Here is how to use it:
```bash
# level_000 can be an existing map or a new one. Don't add an extension, nor a path. It will do it automatically
./apple.py level_000
# Have fun!
```
To create a map of a custom size:
```bash
./apple.py level_000 $width $height
```

To use the editor:

* Mouse wheel + drag&drop to move around
* `Left click` to add block (or erase if you've selected the eraser)
* `E` select eraser
* `B` select Blocks (dirt, stone, ...)
* `O` select Object (AK-47, spawn, ...)

You can also select those tools from the left panel.

Don't click outside the map. You will crash.

Press Save to save. (You didn't thought of that, did you?)

To test your map: edit `config.py` and add it in the `LEVELS` dictionnary (make sure the indexes follow each other) and
in `Config.level_stats`. Then, run the game, select your map and hit play! If it crashes, delete `assets/config.json`.

While testing your map, you can edit the map in the map editor and every time you die the map will update in the game.
This way, you don't have to restart the game every time you change something. Pro-tip: change the spawn point to avoid
having to go through the whole map every time.

Before submitting your Merge Request, check the following things:

* Your map contains the following things:
  * A spawn point
  * A Kalachnikov
  * An ending point
  * Some challenge!
* You can actually finish the map in one streak
* You map is in the right place in `config.py`: the maps are sorted by difficulty, make sure yours is in the right spot!
* Your map is closed: the top, left and right walls should be made of stone, the bottom one should be made of simple barbecues
* Your map is fun to play!
* You found a great name for your map
* You are PEP8 compliant :D

##### Code

Have a look at the issues if they are any, otherwise if you have an idea for a feature, drop it in an issue and we'll be
happy to look at it :D

### Contributors

Special thanks to Valentin 'Faweez' for his wonderful contributions to the maps during this project.
