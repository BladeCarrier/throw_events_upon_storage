# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.views.generic.detail import View

from dashing.widgets import Widget


class HTMLWidget(Widget):
    """a widget that draws some Lena from the web. Requires internet connection to get Lena."""

    def get_more_info(self):
        return ''

    def get_updated_at(self):
        return 'a long time ago in galaxy far far away'

    def get_value(self):
        return ""

    def get_context(self):
        return {
            'moreInfo': self.get_more_info(),
            'updatedAt': self.get_updated_at(),
            'value':self.get_value(),
        }

