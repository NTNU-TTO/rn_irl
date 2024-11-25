# -*- coding: utf-8 -*-
"""
Copyright (c) Lodve Berre and NTNU Technology Transfer AS 2024.

This file is part of Really Nice IRL.

Really Nice IRL is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
 any later version.

Really Nice IRL is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Really Nice IRL. If not, see:
<https://www.gnu.org/licenses/agpl-3.0.html>.
"""

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np

from scipy.interpolate import interp1d
from statistics import mean

KTH = "KTH Innovation\nReadiness Level™"

IRL_CMAP = mc.LinearSegmentedColormap.from_list("IRL_CMAP",
                                                [(0.0000, "#A8202F"),
                                                 (0.1111, "#A8202F"),
                                                 (0.2222, "#D66016"),
                                                 (0.3333, "#F99B08"),
                                                 (0.4444, "#FCB927"),
                                                 (0.5555, "#FDDE16"),
                                                 (0.6666, "#D5D311"),
                                                 (0.7777, "#71AF34"),
                                                 (0.8888, "#37913B"),
                                                 (0.9999, "#37953B"),
                                                 (1.0000, "#37953B")])


def plot_irl(irl_data, smooth=False, dark_mode=True, targets=False):

    if dark_mode:

        fc = '#E5E8EE'
        fg = '#222834'

    else:

        fc = 'black'
        fg = 'white'

    fig, ax = plt.subplots()

    irl_vals = [irl_data.crl,
                irl_data.trl,
                irl_data.brl,
                irl_data.iprl,
                irl_data.tmrl,
                irl_data.frl]

    irl_targets = [irl_data.crl_target,
                   irl_data.trl_target,
                   irl_data.brl_target,
                   irl_data.iprl_target,
                   irl_data.tmrl_target,
                   irl_data.frl_target]

    irl_labels = ['Customer Readiness Level',
                  'Technology Readiness Level',
                  'Business Model Readiness Level',
                  'IPR Readiness Level',
                  'Team Readiness Level',
                  'Funding Readiness Level']

    irl_cats = np.arange(-2*np.pi+np.pi/2, np.pi/2, np.pi/3)*-1
    irl_cats += np.pi
    xs = []
    ys = []
    xts = []
    yts = []
    sxs = []
    sys = []
    sxts = []
    syts = []

    m_x, m_y = np.meshgrid(np.linspace(-1, 1, 256), np.linspace(-1, 1, 256))
    R = np.sqrt((m_x)**2 + (m_y)**2)
    R *= 9/R.max()
#    irl_norm = mc.Normalize(0.5, 5)
    irl_norm = mc.Normalize(1.0, 5.5)

    ax.text(0,
            0,
            KTH,
            size=5,
            ha="center",
            va="center",
            color="white")
#            path_effects=[pe.withStroke(linewidth=1,
#                                        foreground=fg)])

    for i in range(2, 11):

        circle = plt.Circle((0, 0),
                            i,
                            edgecolor=fc,
                            facecolor=None,
                            zorder=None,
                            fill=False,
                            linestyle=':')
        ax.add_patch(circle)

    # Plot spokes and labels.
    for irl_cat, irl_label in zip(irl_cats, irl_labels):

        x = np.cos(irl_cat)*11
        xx = np.cos(irl_cat)*2
        y = np.sin(irl_cat)*11
        yy = np.sin(irl_cat)*2
        ax.plot([x, xx], [y, yy], color=fc, linestyle=':', linewidth=0.5)

        # IRL labels.
        rotation = int(np.rad2deg(irl_cat)-90)

        if rotation == 180:

            ax.text(x,
                    y,
                    irl_label.replace(" ", "\n")+"\n\n",
                    size=8,
                    rotation=0,
                    ha="center",
                    va="top",
                    color=fc)

        else:

            ax.text(x,
                    y,
                    irl_label.replace(" ", "\n")+"\n\n",
                    size=8,
                    rotation=rotation,
                    ha="center",
                    va="center",
                    color=fc)

    # Calculate IRL positions values.
    for irl_val, irl_cat in zip(irl_vals, irl_cats):

        x = np.cos(irl_cat)*(irl_val + 1)
        y = np.sin(irl_cat)*(irl_val + 1)

        xs.append(x)
        ys.append(y)

        # Level labels.
        ax.text(x,
                y,
                "%d" % irl_val,
                size=8,
                ha="center",
                va="center",
                color=fc,
                path_effects=[pe.withStroke(linewidth=2,
                                            foreground=fg)])

    xs.append(xs[0])
    ys.append(ys[0])

    if irl_data.plot_targets or targets:

        for irl_t_val, irl_cat in zip(irl_targets, irl_cats):

            xt = np.cos(irl_cat)*(irl_t_val + 1)
            yt = np.sin(irl_cat)*(irl_t_val + 1)
            xts.append(xt)
            yts.append(yt)

        xts.append(xts[0])
        yts.append(yts[0])

        # Adding average values between the levels for better smoothing.
        for i in range(len(xs)):

            if i < len(xs)-1:

                sxts.append(xts[i])
                syts.append(yts[i])
                sxts.append((xts[i]+xts[i+1])/2.0)
                syts.append((yts[i]+yts[i+1])/2.0)

        sxts.append(sxts[0])
        syts.append(syts[0])

        # Smooth IRL target levels
        orig_t_len = len(sxts)
        sxts = sxts[-3:-1] + sxts + sxts[1:3]
        syts = syts[-3:-1] + syts + syts[1:3]
        tt = np.arange(len(sxts))
        tti = np.linspace(2, orig_t_len+1, 10 * orig_t_len)
        xti = interp1d(tt, sxts, kind='cubic')(tti)
        yti = interp1d(tt, syts, kind='cubic')(tti)
        irl_t = patches.Polygon(np.asarray([xti, yti]).T,
                                linestyle='--',
                                fill=False)

    if smooth:

        # Adding average values between the levels for better smoothing.
        for i in range(len(xs)):

            if i < len(xs)-1:

                sxs.append(xs[i])
                sys.append(ys[i])
                sxs.append((xs[i]+xs[i+1])/2.0)
                sys.append((ys[i]+ys[i+1])/2.0)

        sxs.append(sxs[0])
        sys.append(sys[0])

        # Smooth IRL levels.
        orig_len = len(sxs)
        sxs = sxs[-3:-1] + sxs + sxs[1:3]
        sys = sys[-3:-1] + sys + sys[1:3]
        t = np.arange(len(sxs))
        ti = np.linspace(2, orig_len+1, 10 * orig_len)
        xi = interp1d(t, sxs, kind='cubic')(ti)
        yi = interp1d(t, sys, kind='cubic')(ti)
        irl = patches.Polygon(np.asarray([xi, yi]).T, fill=False)

    else:

        irl = patches.Polygon(np.asarray([xs, ys]).T, fill=False)
        irl_t = patches.Polygon(np.asarray([xts, yts]).T,
                                fill=False,
                                ec=(1, 0, 1, 0.5),
                                fc=(1, 0, 1, 0.5),
                                color=(1, 0, 1, 0.5))
        irl_t.set_edge_color('w')
        irl_t.set_face_color('w')
        irl_t.set_color('w')

    if irl_data.plot_targets or targets:

        ax.add_patch(irl_t)
        ax.imshow(R,
                  cmap=IRL_CMAP,
                  norm=irl_norm,
                  extent=(-10, 10, -10, 10),
                  origin="lower",
                  clip_on=True,
                  clip_path=irl_t,
                  alpha=0.333)

    ax.add_patch(irl)
    ax.imshow(R,
              cmap=IRL_CMAP,
              norm=irl_norm,
              extent=(-10, 10, -10, 10),
              origin="lower",
              clip_on=True,
              clip_path=irl,
              alpha=0.999)
    ax.set_xlim([-11, 11])
    ax.set_ylim([-11, 11])
    ax.set_aspect('equal', adjustable='box')

    fig.patch.set_facecolor('none')
    ax.patch.set_facecolor('none')
    plt.axis('off')

    return fig


def plot_irl_progress(irl0, irl1, smooth=False, dark_mode=True):

    if dark_mode:

        fc = '#E5E8EE'
        fg = '#222834'

    else:

        fc = 'black'
        fg = 'white'

    fig, ax = plt.subplots()
    irl_norm = mc.Normalize(0, 9)

    irl0 = [irl0.crl,
            irl0.trl,
            irl0.brl,
            irl0.iprl,
            irl0.tmrl,
            irl0.frl]

    # Get the mean for the fill color.
    irl0_mean = irl_norm(mean(irl0))

    irl1 = [irl1.crl,
            irl1.trl,
            irl1.brl,
            irl1.iprl,
            irl1.tmrl,
            irl1.frl]

    # Get the mean for fill color.
    irl1_mean = irl_norm(mean(irl1))

    irl_labels = ['Customer Readiness Level',
                  'Technology Readiness Level',
                  'Business Model Readiness Level',
                  'IPR Readiness Level',
                  'Team Readiness Level',
                  'Funding Readiness Level']

    irl_cats = np.arange(-2*np.pi+np.pi/2, np.pi/2, np.pi/3)*-1
    irl_cats += np.pi
    x0s = []
    y0s = []
    x1s = []
    y1s = []

    m_x, m_y = np.meshgrid(np.linspace(-1, 1, 256), np.linspace(-1, 1, 256))
    R = np.sqrt((m_x)**2 + (m_y)**2)
    R *= 9/R.max()

    for i in range(1, 10):

        circle = plt.Circle((0, 0),
                            i,
                            edgecolor=fc,
                            facecolor=None,
                            zorder=None,
                            fill=False,
                            linestyle=':')
        ax.add_patch(circle)

    # Plot spokes and labels.
    for irl_cat, irl_label in zip(irl_cats, irl_labels):

        x = np.cos(irl_cat)*10
        y = np.sin(irl_cat)*10
        ax.plot([x, 0],
                [y, 0],
                color=fc,
                linestyle=':',
                linewidth=0.5)

        # IRL labels.
        rotation = int(np.rad2deg(irl_cat)-90)

        if rotation == 180:

            ax.text(x,
                    y,
                    irl_label.replace(" ", "\n")+"\n\n",
                    size=8,
                    rotation=0,
                    ha="center",
                    va="top",
                    color=fc)

        else:

            ax.text(x,
                    y,
                    irl_label.replace(" ", "\n")+"\n\n",
                    size=8,
                    rotation=rotation,
                    ha="center",
                    va="center",
                    color=fc)

    # Calculate IRL positions values.
    for irl0_val, irl1_val, irl_cat in zip(irl0, irl1, irl_cats):

        x0 = np.cos(irl_cat)*irl0_val
        y0 = np.sin(irl_cat)*irl0_val
        x1 = np.cos(irl_cat)*irl1_val
        y1 = np.sin(irl_cat)*irl1_val

        x0s.append(x0)
        y0s.append(y0)
        x1s.append(x1)
        y1s.append(y1)

        # Level labels.
        ax.text(x1,
                y1,
                "%d" % irl1_val,
                size=8,
                ha="center",
                va="center",
                color=fc,
                path_effects=[pe.withStroke(linewidth=2,
                                            foreground=fg)])

    x0s.append(x0s[0])
    y0s.append(y0s[0])
    x1s.append(x1s[0])
    y1s.append(y1s[0])

    if smooth:

        sx0s = []
        sy0s = []
        sx1s = []
        sy1s = []

        # Adding average values between the levels for better smoothing.
        for i in range(len(x0s)):

            if i < len(x0s)-1:

                sx0s.append(x0s[i])
                sy0s.append(y0s[i])
                sx0s.append((x0s[i]+x0s[i+1])/2.0)
                sy0s.append((y0s[i]+y0s[i+1])/2.0)

                sx1s.append(x1s[i])
                sy1s.append(y1s[i])
                sx1s.append((x1s[i]+x1s[i+1])/2.0)
                sy1s.append((y1s[i]+y1s[i+1])/2.0)

        sx0s.append(sx0s[0])
        sy0s.append(sy0s[0])
        sx1s.append(sx1s[0])
        sy1s.append(sy1s[0])

        # Smooth IRL0 levels.
        orig_len = len(sx0s)
        sx0s = sx0s[-3:-1] + sx0s + sx0s[1:3]
        sy0s = sy0s[-3:-1] + sy0s + sy0s[1:3]
        t = np.arange(len(sx0s))
        ti = np.linspace(2, orig_len+1, 10 * orig_len)
        xi = interp1d(t, sx0s, kind='cubic')(ti)
        yi = interp1d(t, sy0s, kind='cubic')(ti)

        # Smooth IRL1 levels
        orig_t_len = len(sx1s)
        sx1s = sx1s[-3:-1] + sx1s + sx1s[1:3]
        sy1s = sy1s[-3:-1] + sy1s + sy1s[1:3]
        tt = np.arange(len(sx1s))
        tti = np.linspace(2, orig_t_len+1, 10 * orig_t_len)
        xti = interp1d(tt, sx1s, kind='cubic')(tti)
        yti = interp1d(tt, sy1s, kind='cubic')(tti)

        # Previous IRL.
        irl0 = patches.Polygon(np.asarray([xi, yi]).T,
                               facecolor=IRL_CMAP(irl0_mean),
                               edgecolor='black',
                               linestyle='--',
                               alpha=0.888)

        irl1 = patches.Polygon(np.asarray([xti, yti]).T,
                               facecolor=IRL_CMAP(irl1_mean),
                               edgecolor='black',
                               alpha=0.888)

    else:

        irl0 = patches.Polygon(np.asarray([x0s, y0s]).T, fill=False)
        irl0.set_edge_color(IRL_CMAP(irl0_mean))
        irl0.set_face_color(IRL_CMAP(irl0_mean))
        irl0.set_color(IRL_CMAP(irl0_mean))
        irl1 = patches.Polygon(np.asarray([x1s, y1s]).T,
                               fill=False,
                               ec=(1, 0, 1, 0.5),
                               fc=(1, 0, 1, 0.5),
                               color=(1, 0, 1, 0.5))

    ax.add_patch(irl1)
    ax.add_patch(irl0)

    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_aspect('equal', adjustable='box')
    fig.patch.set_facecolor('none')
    ax.patch.set_facecolor('none')
    plt.axis('off')

    return fig
