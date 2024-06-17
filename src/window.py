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
        self.add_grid_size(row_quantity = self.grid_row_quantity, column_quantity = self.grid_column_quantity)

        style_provider = Gtk.CssProvider()
        resource_path_style = '/com/github/SamuelSchlemperSchlemuel/SingWriter/style.css'
        style_provider.load_from_path(f'resource://{resource_path_style}')

        scrollable_content = Gtk.Label(label="CLorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc. \n" * 5)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(scrollable_content)
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

    def add_grid_size(self, row_quantity, column_quantity):
        for num in range(row_quantity):
            self.grid.insert_row(num)

        for num in range(column_quantity):
            self.grid.insert_column(num)

        for row in range(row_quantity):
            for column in range(column_quantity):
                box = Gtk.Box()
                box.get_style_context().add_class('box')
                self.grid.attach(box, column, row, 1, 1)

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
        
