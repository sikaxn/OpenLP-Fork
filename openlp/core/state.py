# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################

"""
The :mod:`core` module provides state management

All the core functions of the OpenLP application including the GUI, settings, logging and a plugin framework are
contained within the openlp.core module.
"""
import logging
from enum import IntEnum

from openlp.core.common import Singleton
from openlp.core.common.registry import Registry
from openlp.core.common.mixins import LogMixin
from openlp.core.lib.plugin import Plugin, PluginStatus


log = logging.getLogger()


class MessageType(IntEnum):
    Error = 1
    Warning = 2
    Information = 3


class StateModule(LogMixin):
    def __init__(self):
        """
        Holder of State information per module
        """
        super(StateModule, self).__init__()
        self.name: str | None = None
        self.order: int = 0
        self.is_plugin: bool = False
        self.status: PluginStatus = PluginStatus.Inactive
        self.pass_preconditions: bool = False
        self.requires: str | None = None
        self.required_by: list | None = None
        self.text: str | None = None
        self.message_type: MessageType = MessageType.Error


class State(LogMixin, metaclass=Singleton):

    def load_settings(self):
        self.modules = {}

    def save_settings(self):
        pass

    def add_service(self, name: str, order: int, is_plugin: bool = False, status: PluginStatus = PluginStatus.Active,
                    requires: str | None = None):
        """
        Add a module to the array and load dependencies.  There will only be one item per module
        :param name: Module name
        :param order: Order to display
        :param is_plugin: Am I a plugin
        :param status: The active status
        :param requires: Module name this requires
        :return:
        """
        if name not in self.modules:
            state = StateModule()
            state.name = name
            state.order = order
            state.is_plugin = is_plugin
            state.status = status
            state.requires = requires
            state.required_by = []
            self.modules[name] = state
            if requires and requires in self.modules:
                if requires not in self.modules[requires].required_by:
                    self.modules[requires].required_by.append(name)

    def missing_text(self, name: str, text: str, type_: MessageType = MessageType.Error):
        """
        Updates the preconditions state of a module

        :param name: Module name
        :param text: Module missing text
        :return:
        """
        self.modules[name].text = text
        self.modules[name].message_type = type_

    def get_text(self, type_: MessageType | None = None) -> str:
        """
        return an string of error text
        :return: a string of text
        """
        all_text = ''
        for mod in self.modules:
            if self.modules[mod].text and (not type_ or self.modules[mod].message_type == type_):
                all_text = all_text + self.modules[mod].text + '\n'
        return all_text

    def update_pre_conditions(self, name: str, is_active: bool):
        """
        Updates the preconditions state of a module

        :param name: Module name
        :param is_active: Module new status
        :return:
        """
        self.modules[name].pass_preconditions = is_active
        if self.modules[name].is_plugin:
            plugin = Registry().get(f'{name}_plugin')
            if is_active:
                self.log_debug(f'Plugin {plugin.name} active')
                plugin.set_status()
            else:
                plugin.status = PluginStatus.Disabled

    def flush_preconditions(self):
        """
        Now all modules are loaded lets update all the preconditions.

        :return:
        """
        for mods in self.modules:
            for req in self.modules[mods].required_by:
                self.modules[req].pass_preconditions = self.modules[mods].pass_preconditions
        plugins_list = sorted(self.modules, key=lambda state: self.modules[state].order)
        mdl = {}
        for pl in plugins_list:
            mdl[pl] = self.modules[pl]
        self.modules = mdl

    def is_module_active(self, name: str) -> bool:
        """
        Checks if a modules is active.

        :param name: Module name
        :return: Have the preconditions been met.
        :rtype: bool
        """
        return self.modules[name].status == PluginStatus.Active

    def check_preconditions(self, name: str) -> bool:
        """
        Checks if a modules preconditions have been met.

        :param name: Module name
        :return: Have the preconditions been met.
        :rtype: bool
        """
        try:
            if self.modules[name].requires is None:
                return self.modules[name].pass_preconditions
            else:
                mod = self.modules[name].requires
                return self.modules[mod].pass_preconditions
        except KeyError:
            # Module is missing so therefore not found.
            return False

    def list_plugins(self) -> list[Plugin]:
        """
        Return a list of plugins
        :return: an array of plugins
        """
        plugins = []
        for mod in self.modules:
            if self.modules[mod].is_plugin:
                plugins.append(Registry().get(f'{mod}_plugin'))
        return plugins
