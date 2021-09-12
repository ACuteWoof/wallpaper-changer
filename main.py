#!/bin/python3

import gi
import os
import json
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

if os.getenv("WALLPAPER_FOLDER") == None:
    os.environ["WALLPAPER_FOLDER"] = "~/Pictures/wallpapers"
    wallpaper_location = os.getenv("WALLPAPER_FOLDER")
else:
    wallpaper_location = os.getenv("WALLPAPER_FOLDER")


class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="Wallpaper Changer For Manjaro Qtile Edition")
        self.set_border_width(10)
        self.set_default_size(700, 400)

        self.header = Gtk.HeaderBar()
        self.header.props.show_close_button = False

        self.set_titlebar(self.header)

        pane_position = 300

        self.main_box = Gtk.Box()
        self.main_box.set_margin_bottom(0)

        self.image_preview = Gtk.Image()
        self.image_preview.set_size_request(400, 400)

        self.apply_button = Gtk.Button()
        self.apply_button.set_size_request(0, 0)
        self.apply_button.set_label("Apply as Wallpaper")

        self.request_walls_btn = Gtk.Button()
        self.request_walls_btn.set_size_request(0, 0)
        self.request_walls_btn.set_label("Load Wallpapers")

        self.header.pack_start(Gtk.Label("Wallpaper Chooser"))
        self.header.pack_end(self.apply_button)
        self.header.pack_end(self.request_walls_btn)
        self.main_box.add(self.image_preview)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.pane = Gtk.Paned()
        self.pane.set_orientation(Gtk.Orientation.VERTICAL)

        self.pane.set_position(pane_position)
        self.add(self.pane)
        self.pane.add1(self.main_box)
        self.pane.add2(self.scrolled)

        self.wallpaper_request_thread = threading.Thread(
            target=self.create_flowbox, args=(1,), daemon=True
        )

        self.request_walls_btn.connect("clicked", self.start_wallpaper_thread)

        self.show_all()

    def start_wallpaper_thread(self, *_button):
        self.wallpaper_request_thread.start()
        # self.wallpaper_request_thread.join()

    def get_files(self, search_path):
        for (dirpath, _, filenames) in os.walk(search_path):
            for filename in filenames:
                yield os.path.join(dirpath, filename)

    def add_wallpaper(self, wallpaper):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            wallpaper, width=220, height=220, preserve_aspect_ratio=True
        )

        btn = Gtk.EventBox()
        btn.connect("button-press-event", self.preview_image, wallpaper)

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        btn.add(image)
        return btn

    def preview_image(self, box, *data):

        wallpaper = data[1]

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            wallpaper, width=400, height=400, preserve_aspect_ratio=True
        )
        print(wallpaper)
        self.image_preview.set_from_pixbuf(pixbuf)
        self.apply_button.set_size_request(50, 5)
        self.apply_button.connect("clicked", self.set_wallpaper, wallpaper)

    def create_flowbox(self, *button):
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(30)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        unfiltered_wallpaper_files = self.get_files(
            wallpaper_location.replace("~", os.getenv("HOME"))
        )

        wallpapers = []

        for wallpaper_file in unfiltered_wallpaper_files:
            if wallpaper_file.split(".")[-1] in ["jpg", "png"]:
                wallpapers.append(wallpaper_file)

        for wallpaper in wallpapers:
            card = self.add_wallpaper(wallpaper)
            self.flowbox.add(card)

        self.scrolled.add(self.flowbox)
        self.flowbox.show_all()

    def set_wallpaper(self, button, *data):
        wallpaper = data[0]
        os.system(f"xwallpaper --zoom {wallpaper}")
        with open(
            "{}/.config/qtile/config/settings.json".format(os.getenv("HOME"))
        ) as settings_file:
            settings = json.load(settings_file)

        settings["looks"]["wallpaper"] = wallpaper
        print(f"WALLPAPER: {settings['looks']['wallpaper']}")

        json.dump(
            settings,
            fp=open(
                "{}/.config/qtile/config/settings.json".format(os.getenv("HOME")), "w"
            ),
        )

        print(wallpaper)


def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show()
    Gtk.main()


if __name__ == "__main__":
    main()
