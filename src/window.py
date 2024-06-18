# window.py
#
# Copyright 2024 Schlemuel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk, Gio, Gdk

@Gtk.Template(resource_path='/com/github/SamuelSchlemperSchlemuel/SingWriter/window.ui')
class SingwriterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'SingwriterWindow'

    grid = Gtk.Template.Child()
    symbol_screen_button = Gtk.Template.Child()
    symbol_screen = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid_row_quantity = 6
        self.grid_column_quantity = 10
        self.add_grid_size(grid = self.grid,
                           row_quantity = self.grid_row_quantity,
                           column_quantity = self.grid_column_quantity,
                           boxes = True)

        style_provider = Gtk.CssProvider()
        resource_path_style = '/com/github/SamuelSchlemperSchlemuel/SingWriter/style.css'
        style_provider.load_from_path(f'resource://{resource_path_style}')

        self.symbol_screen_content()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.symbol_screen_grid)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)

        self.revealer = Gtk.Revealer()
        self.revealer.set_child(scrolled_window)
        self.revealer.set_reveal_child(False)
        self.revealer.set_vexpand(True)
        self.revealer.set_hexpand(True)

        self.symbol_screen.append(self.revealer)

        kwargs['application'].create_action('change-size', self.change_grid_size)
        self.symbol_screen_button.connect('clicked', self.push_screen)

    def add_grid_size(self, grid, row_quantity, column_quantity, boxes):
        for num in range(row_quantity):
            grid.insert_row(num)

        for num in range(column_quantity):
            grid.insert_column(num)


        for row in range(row_quantity):
            for column in range(column_quantity):
                box = Gtk.Box()

                if boxes:
                    box.get_style_context().add_class('box')

                grid.attach(box, column, row, 1, 1)

    def change_grid_size(self, widget, _):
        dialog = GridSizeDialog(self)
        dialog.show()

    def remove_grid_children(self):
        if self.grid_row_quantity < self.grid_column_quantity:
            for num in range(self.grid_row_quantity):
                self.grid.remove_row(0)
        else:
            for num in range(self.grid_column_quantity):
                self.grid.remove_column(0)

    def push_screen(self, widget):
        current_reveal_state = self.revealer.get_reveal_child()

        if not current_reveal_state:
            self.revealer.get_style_context().add_class('revealer')
            self.symbol_screen_button.set_icon_name('pan-down-symbolic')
        else:
            self.revealer.get_style_context().remove_class('revealer')
            self.symbol_screen_button.set_icon_name('pan-up-symbolic')

        self.revealer.set_reveal_child(not current_reveal_state)

    def symbol_screen_content(self):
        self.hand_format = Gtk.Button(label="Formato da mão")
        self.movement = Gtk.Button(label="Movimento")
        self.facial_expression = Gtk.Button(label="Expressão facial")
        self.transformation = Gtk.Button(label="Transformação")

        self.hand_format.connect('clicked', self.hand_format_screen)
        self.movement.connect('clicked', self.movement_screen)
        self.facial_expression.connect('clicked', self.facial_expression_screen)
        self.transformation.connect('clicked', self.transformation_screen)

        self.hand_format.get_style_context().add_class('button_content_revealer')
        self.movement.get_style_context().add_class('button_content_revealer')
        self.facial_expression.get_style_context().add_class('button_content_revealer')
        self.transformation.get_style_context().add_class('button_content_revealer')

        self.symbol_screen_grid = Gtk.Grid()
        self.symbol_screen_grid.set_column_homogeneous(True)
        self.symbol_screen_grid.set_row_homogeneous(True)
        self.symbol_screen_grid.set_column_spacing(5)
        self.symbol_screen_grid.set_row_spacing(10)

        self.symbol_screen_grid_row_quantity = 16
        self.symbol_screen_grid_column_quantity = 8

        self.add_grid_size(grid = self.symbol_screen_grid,
                           row_quantity = self.symbol_screen_grid_row_quantity,
                           column_quantity = self.symbol_screen_grid_column_quantity,
                           boxes = False)

        self.hand_format.emit('clicked')

    def clean_symbol_screen_grid(self):
        for row in range(self.symbol_screen_grid_row_quantity):
            for column in range(self.symbol_screen_grid_column_quantity):
                child = self.symbol_screen_grid.get_child_at(column, row)
                self.symbol_screen_grid.remove(child)

                if self.hand_format.get_parent():
                    self.hand_format.get_parent().remove(self.hand_format)

                if self.movement.get_parent():
                    self.movement.get_parent().remove(self.movement)

                if self.facial_expression.get_parent():
                    self.facial_expression.get_parent().remove(self.facial_expression)

                if self.transformation.get_parent():
                    self.transformation.get_parent().remove(self.transformation)

        self.add_grid_size(grid = self.symbol_screen_grid,
                           row_quantity = self.symbol_screen_grid_row_quantity,
                           column_quantity = self.symbol_screen_grid_column_quantity,
                           boxes = False)

        self.symbol_screen_grid.attach(self.hand_format,       column = 0, row = 0, width = 2, height = 1)
        self.symbol_screen_grid.attach(self.movement,          column = 2, row = 0, width = 2, height = 1)
        self.symbol_screen_grid.attach(self.facial_expression, column = 4, row = 0, width = 2, height = 1)
        self.symbol_screen_grid.attach(self.transformation,    column = 6, row = 0, width = 2, height = 1)

    def add_characters(self, characters):
        row = 1
        col = 0

        for char in characters:
            label = Gtk.Label(label=char)
            label.get_style_context().add_class('character_label')

            box = Gtk.Box()
            box.append(label)

            child = self.symbol_screen_grid.get_child_at(col, row)
            self.symbol_screen_grid.remove(child)
            self.symbol_screen_grid.attach(box, col, row, 1, 1)
            col += 1

            if col >= self.symbol_screen_grid_column_quantity:
                col = 0
                row += 1

    def hand_format_screen(self, widget):
        self.clean_symbol_screen_grid()

        characters = ['𝠀', '𝠁', '𝠂']

        self.add_characters(characters)


    def movement_screen(self, widget):
        self.clean_symbol_screen_grid()

    def facial_expression_screen(self, widget):
        self.clean_symbol_screen_grid()

    def transformation_screen(self, widget):
        self.clean_symbol_screen_grid()

class GridSizeDialog(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(title="Mudar tamanho da grade", transient_for=parent, modal=True)
        self.parent = parent

        adjustment_row = Gtk.Adjustment(value=1, lower=1, upper=100, step_increment=1, page_increment=10, page_size=0)
        self.spin_button_row = Gtk.SpinButton()
        self.spin_button_row.set_adjustment(adjustment_row)
        self.spin_button_row.set_numeric(True)

        adjustment_column = Gtk.Adjustment(value=1, lower=1, upper=100, step_increment=1, page_increment=10, page_size=0)
        self.spin_button_column = Gtk.SpinButton()
        self.spin_button_column.set_adjustment(adjustment_column)
        self.spin_button_column.set_numeric(True)

        button = Gtk.Button(label='Mudar tamanho da grade')
        button.connect('clicked', self.actualize_grid_size)

        label_row = Gtk.Label(label='Quantidade de linhas')
        label_column = Gtk.Label(label='Quantidade de colunas')

        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        box.append(label_row)
        box.append(self.spin_button_row)
        box.append(label_column)
        box.append(self.spin_button_column)
        box.append(button)

        content_area = self.get_content_area()
        content_area.append(box)

    def actualize_grid_size(self, widget):
        self.parent.remove_grid_children()
        self.parent.grid_row_quantity = self.spin_button_row.get_value_as_int()
        self.parent.grid_column_quantity = self.spin_button_column.get_value_as_int()
        self.parent.add_grid_size(row_quantity = self.parent.grid_row_quantity, column_quantity = self.parent.grid_column_quantity)
        self.response(Gtk.ResponseType.OK)
        
