import os

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, ViewerSelectMixin
from jdaviz.core.user_api import PluginUserApi

__all__ = ['ExportViewer']


@tray_registry('g-export-plot', label="Export Plot")
class ExportViewer(PluginTemplateMixin, ViewerSelectMixin):
    """
    See the :ref:`Export Plot Plugin Documentation <imviz-export-plot>` for more details.

    Only the following attributes and methods are available through the
    :ref:`public plugin API <plugin-apis>`:

    * ``viewer`` (:class:`~jdaviz.core.template_mixin.ViewerSelect`):
      Viewer to select for exporting the figure image.
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.show`
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.open_in_tray`
    * :meth:`save_figure`
    """
    template_file = __file__, "export_plot.vue"

    @property
    def user_api(self):
        return PluginUserApi(self, expose=('viewer', 'save_figure'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_figure(self, filename=None, filetype=None):
        """
        Save the figure to an image with a provided filename or through an interactive save dialog.

        If ``filetype`` is 'png' (or defaults to 'png' based on ``filename``), the interactive save
        dialog will be bypassed (this is not supported for 'svg').

        Parameters
        ----------
        filename : str or `None`
            Filename to autopopulate the save dialog.
        filetype : {'png', 'svg', `None`}
            Filetype (PNG or SVG).  If `None`, will default based on filename or to PNG.

        """
        if filetype is None:
            if filename is not None and '.' in filename:
                filetype = filename.split('.')[-1]
            else:
                # default to png
                filetype = 'png'

        viewer = self.viewer.selected_obj
        if filetype == "png":
            if filename is None:
                viewer.figure.save_png()
            else:
                # support writing without save dialog
                # https://github.com/bqplot/bqplot/pull/1397
                def on_img_received(data):
                    with open(os.path.expanduser(filename), 'bw') as f:
                        f.write(data)
                viewer.figure.get_png_data(on_img_received)
        elif filetype == "svg":
            viewer.figure.save_svg(filename)
        else:
            raise NotImplementedError(f"filetype={filetype} not supported")

    def vue_save_figure(self, filetype):
        """
        Callback for save figure events in the front end viewer toolbars. Uses
        the bqplot.Figure save methods.
        """
        self.save_figure(filetype=filetype)
