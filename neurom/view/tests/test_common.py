# Copyright (c) 2015, Ecole Polytechnique Federale de Lausanne, Blue Brain Project
# All rights reserved.
#
# This file is part of NeuroM <https://github.com/BlueBrain/NeuroM>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#     3. Neither the name of the copyright holder nor the names of
#        its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from nose import tools as nt

from neurom.view.common import (plt, figure_naming, get_figure, save_plot, plot_style,
                                plot_title, plot_labels, plot_legend, plot_limits, plot_ticks,
                                plot_sphere, get_color, plot_cylinder)

from neurom.core.types import NeuriteType

import shutil
import tempfile

from contextlib import contextmanager

import numpy as np


def test_figure_naming():
    pretitle, posttitle, prefile, postfile = figure_naming(pretitle='Test', posttitle=None, prefile="", postfile=3)
    nt.eq_(pretitle, 'Test -- ')
    nt.eq_(posttitle, "")
    nt.eq_(prefile, "")
    nt.eq_(postfile, "_3")

    pretitle, posttitle, prefile, postfile = figure_naming(pretitle='', posttitle="Test", prefile="test", postfile="")
    nt.eq_(pretitle, "")
    nt.eq_(posttitle, " -- Test")
    nt.eq_(prefile, "test_")
    nt.eq_(postfile, "")


def test_get_figure():
    fig_old = plt.figure()
    fig, ax = get_figure(new_fig=False, subplot=False)
    nt.eq_(fig, fig_old)
    nt.eq_(ax.colNum, 0)
    nt.eq_(ax.rowNum, 0)

    fig1, ax1 = get_figure(new_fig=True, subplot=224)
    nt.ok_(fig1 != fig_old)
    nt.eq_(ax1.colNum, 1)
    nt.eq_(ax1.rowNum, 1)

    fig = get_figure(new_fig=True, no_axes=True)
    nt.eq_(type(fig), plt.Figure)

    fig2, ax2 = get_figure(new_fig=True, subplot=[1, 1, 1])
    nt.eq_(ax2.colNum, 0)
    nt.eq_(ax2.rowNum, 0)
    plt.close('all')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig2, ax2 = get_figure(new_fig=False, new_axes=False)
    nt.eq_(fig2, plt.gcf())
    nt.eq_(ax2, plt.gca())
    plt.close('all')


def test_save_plot():
    fig_name = 'Figure.png'

    tempdir = tempfile.mkdtemp('test_common')
    try:
        old_dir = os.getcwd()
        os.chdir(tempdir)

        fig_old = plt.figure()
        fig = save_plot(fig_old)
        nt.ok_(os.path.isfile(fig_name))

        os.remove(fig_name)

        fig = save_plot(fig_old, output_path='subdir')
        nt.ok_(os.path.isfile(os.path.join(tempdir, 'subdir', fig_name)))
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tempdir)
        plt.close('all')


@contextmanager
def get_fig_2d():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot([0, 0], [1, 2], label='test')
    yield fig, ax
    plt.close(fig)


@contextmanager
def get_fig_3d():
    fig0 = plt.figure()
    ax0 = fig0.add_subplot((111), projection='3d')
    ax0.plot([0, 0], [1, 2], [2, 1])
    yield fig0, ax0
    plt.close(fig0)


def test_plot_title():
    with get_fig_2d() as (fig, ax):
        plot_title(ax)
        nt.eq_(ax.get_title(), 'Figure')

    with get_fig_2d() as (fig, ax):
        plot_title(ax, title='Test')
        nt.eq_(ax.get_title(), 'Test')


def test_plot_labels():
    with get_fig_2d() as (fig, ax):
        plot_labels(ax)
        nt.eq_(ax.get_xlabel(), 'X')
        nt.eq_(ax.get_ylabel(), 'Y')

    with get_fig_2d() as (fig, ax):
        plot_labels(ax, xlabel='T', ylabel='R')
        nt.eq_(ax.get_xlabel(), 'T')
        nt.eq_(ax.get_ylabel(), 'R')

    with get_fig_3d() as (fig0, ax0):
        plot_labels(ax0)
        nt.eq_(ax0.get_zlabel(), 'Z')

    with get_fig_3d() as (fig0, ax0):
        plot_labels(ax0, zlabel='T')
        nt.eq_(ax0.get_zlabel(), 'T')


def test_plot_legend():
    with get_fig_2d() as (fig, ax):
        plot_legend(ax)
        legend = ax.get_legend()
        nt.ok_(legend is None)

    with get_fig_2d() as (fig, ax):
        plot_legend(ax, no_legend=False)
        legend = ax.get_legend()
        nt.eq_(legend.get_texts()[0].get_text(), 'test')


def test_plot_limits():
    with get_fig_2d() as (fig, ax):
        plot_limits(ax)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        nt.eq_(ax.get_xlim(), xlim)
        nt.eq_(ax.get_ylim(), ylim)

    with get_fig_2d() as (fig, ax):
        plot_limits(ax, xlim=(0, 100), ylim=(-100, 0))
        nt.eq_(ax.get_xlim(), (0, 100))
        nt.eq_(ax.get_ylim(), (-100, 0))

    with get_fig_3d() as (fig0, ax0):
        plot_limits(ax0)
        zlim0 = ax0.get_zlim()
        nt.ok_(np.allclose(ax0.get_zlim(), zlim0))

    with get_fig_3d() as (fig0, ax0):
        plot_limits(ax0, zlim=(0, 100))
        nt.ok_(np.allclose(ax0.get_zlim(), (0, 100)))


def test_plot_ticks():
    with get_fig_2d() as (fig, ax):
        plot_ticks(ax)
        nt.ok_(len(ax.get_xticks()))
        nt.ok_(len(ax.get_yticks()))

    with get_fig_2d() as (fig, ax):
        plot_ticks(ax, xticks=[], yticks=[])
        nt.eq_(len(ax.get_xticks()), 0)
        nt.eq_(len(ax.get_yticks()), 0)

    with get_fig_2d() as (fig, ax):
        plot_ticks(ax, xticks=np.arange(3), yticks=np.arange(4))
        nt.eq_(len(ax.get_xticks()), 3)
        nt.eq_(len(ax.get_yticks()), 4)

    with get_fig_3d() as (fig0, ax0):
        plot_ticks(ax0)
        nt.ok_(len(ax0.get_zticks()))

    with get_fig_3d() as (fig0, ax0):
        plot_ticks(ax0, zticks=[])
        nt.eq_(len(ax0.get_zticks()), 0)

    with get_fig_3d() as (fig0, ax0):
        plot_ticks(ax0, zticks=np.arange(3))
        nt.eq_(len(ax0.get_zticks()), 3)


def test_plot_style():
    with get_fig_2d() as (fig, ax):
        plot_style(fig, ax)
        nt.eq_(ax.get_title(), 'Figure')
        nt.eq_(ax.get_xlabel(), 'X')
        nt.eq_(ax.get_ylabel(), 'Y')

    with get_fig_2d() as (fig, ax):
        plot_style(fig, ax, no_axes=True)
        nt.ok_(not ax.get_frame_on())
        nt.ok_(not ax.xaxis.get_visible())
        nt.ok_(not ax.yaxis.get_visible())

    with get_fig_2d() as (fig, ax):
        plot_style(fig, ax, tight=True)
        nt.ok_(fig.get_tight_layout())

    with get_fig_2d() as (fig, ax):
        plot_style(fig, ax, show_plot=False)

    try:
        tempdir = tempfile.mkdtemp('test_common')
        with get_fig_2d() as (fig, ax):
            plot_style(fig, ax, output_path=tempdir, output_name='Figure')
        nt.ok_(os.path.isfile(os.path.join(tempdir, 'Figure.png')))
    finally:
        shutil.rmtree(tempdir)


def test_get_color():
    nt.eq_(get_color(None, NeuriteType.basal_dendrite), "red")
    nt.eq_(get_color(None, NeuriteType.axon), "blue")
    nt.eq_(get_color(None, NeuriteType.apical_dendrite), "purple")
    nt.eq_(get_color(None, NeuriteType.soma), "black")
    nt.eq_(get_color(None, NeuriteType.undefined), "green")
    nt.eq_(get_color(None, 'wrong'), "green")
    nt.eq_(get_color('blue', 'wrong'), "blue")
    nt.eq_(get_color('yellow', NeuriteType.axon), "yellow")


def test_plot_cylinder():
    fig0, ax0 = get_figure(params={'projection': '3d'})
    start, end = np.array([0, 0, 0]), np.array([1, 0, 0])
    plot_cylinder(ax0, start=start, end=end,
                  start_radius=0, end_radius=10.,
                  color='black', alpha=1.)
    nt.ok_(ax0.has_data())


def test_plot_sphere():
    fig0, ax0 = get_figure(params={'projection': '3d'})
    plot_sphere(ax0, [0, 0, 0], 10., color='black', alpha=1.)
    nt.ok_(ax0.has_data())
