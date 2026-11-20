"""Centralized Plotly chart factory for the Sales Analytics Workbench.

Ensures visual consistency across all modules by providing a single
source for chart creation, theme application, and styling.
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Workbench Dark Theme Registration
# ---------------------------------------------------------------------------

WORKBENCH_DARK_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        # Paper and plot background
        paper_bgcolor="#0B132B",
        plot_bgcolor="#1C2541",
        # Font
        font=dict(
            family="Segoe UI, Roboto, Helvetica Neue, sans-serif",
            color="#F8FAFC",
            size=12,
        ),
        # Title
        title=dict(
            font=dict(
                family="Segoe UI, Roboto, Helvetica Neue, sans-serif",
                color="#F8FAFC",
                size=16,
            ),
            x=0.02,
            xanchor="left",
        ),
        # Axes
        xaxis=dict(
            gridcolor="#2D3B60",
            zerolinecolor="#2D3B60",
            linecolor="#2D3B60",
            tickfont=dict(color="#94A3B8"),
            title=dict(font=dict(color="#94A3B8")),
        ),
        yaxis=dict(
            gridcolor="#2D3B60",
            zerolinecolor="#2D3B60",
            linecolor="#2D3B60",
            tickfont=dict(color="#94A3B8"),
            title=dict(font=dict(color="#94A3B8")),
        ),
        # Legend
        legend=dict(
            bgcolor="rgba(28, 37, 65, 0.8)",
            bordercolor="#2D3B60",
            borderwidth=1,
            font=dict(color="#F8FAFC"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        # Colorway for discrete traces
        colorway=[
            "#4F86F7",  # Royal Blue
            "#00F5D4",  # Vivid Cyan
            "#F59E0B",  # Amber
            "#EF4444",  # Red
            "#10B981",  # Emerald
            "#A855F7",  # Purple
            "#EC4899",  # Pink
            "#06B6D4",  # Cyan
        ],
        # Hover
        hoverlabel=dict(
            bgcolor="#1C2541",
            bordercolor="#2D3B60",
            font=dict(color="#F8FAFC", size=12),
        ),
        # Margins
        margin=dict(l=60, r=30, t=60, b=50),
        # Modebar
        modebar=dict(
            bgcolor="rgba(28, 37, 65, 0.9)",
            color="#94A3B8",
            activecolor="#4F86F7",
        ),
    )
)


# Register the template globally
pio.templates["workbench_dark"] = WORKBENCH_DARK_TEMPLATE


# ---------------------------------------------------------------------------
# ChartFactory Class
# ---------------------------------------------------------------------------


class ChartFactory:
    """Centralized factory for creating consistently styled Plotly figures.

    All charts produced by this factory use the `workbench_dark` template,
    INR-formatted tooltips, and responsive sizing. This ensures visual
    consistency across the EDA dashboard, SQL analysis, and statistical
    validation modules.

    Usage:
        factory = ChartFactory()
        fig = factory.bar_chart(df, x="Category", y="Revenue", title="Revenue by Category")
    """

    def __init__(self) -> None:
        """Initialize the chart factory."""
        self.default_template = "workbench_dark"

    def _apply_standard_layout(
        self,
        fig: go.Figure,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str | None = None,
        height: int | None = None,
        width: int | None = None,
    ) -> go.Figure:
        """Apply standard layout updates to a figure."""
        updates = {}
        if title:
            updates["title"] = title
        if xaxis_title:
            updates["xaxis_title"] = xaxis_title
        if yaxis_title:
            updates["yaxis_title"] = yaxis_title
        if height:
            updates["height"] = height
        if width:
            updates["width"] = width

        fig.update_layout(updates, template=self.default_template)
        return fig

    def _format_hover_template(
        self,
        x_label: str = "x",
        y_label: str = "y",
        y_is_currency: bool = False,
        y_is_percent: bool = False,
    ) -> str:
        """Generate a hover template string with appropriate formatting.

        Args:
            x_label: Label for x-axis value.
            y_label: Label for y-axis value.
            y_is_currency: If True, format y as INR.
            y_is_percent: If True, format y as percentage.

        Returns:
            Plotly hovertemplate string.
        """
        if y_is_currency:
            y_fmt = "₹%{y:,.2f}"
        elif y_is_percent:
            y_fmt = "%{y:.2f}%"
        else:
            y_fmt = "%{y:,.0f}"

        return f"<b>{x_label}:</b> %{{x}}<br><b>{y_label}:</b> {y_fmt}<extra></extra>"

    # -----------------------------------------------------------------------
    # Bar Charts
    # -----------------------------------------------------------------------

    def bar_chart(
        self,
        df,
        x: str,
        y: str,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str | None = None,
        color: str | None = None,
        color_discrete_sequence: list[str] | None = None,
        orientation: str = "v",
        height: int = 450,
        y_is_currency: bool = False,
        y_is_percent: bool = False,
        text: str | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a vertical or horizontal bar chart.

        Args:
            df: DataFrame containing the data.
            x: Column name for x-axis.
            y: Column name for y-axis.
            title: Chart title.
            xaxis_title: X-axis label.
            yaxis_title: Y-axis label.
            color: Optional column to color bars by.
            color_discrete_sequence: Custom color sequence.
            orientation: "v" for vertical, "h" for horizontal.
            height: Chart height in pixels.
            y_is_currency: Format y-axis as INR in hover.
            y_is_percent: Format y-axis as percentage in hover.
            text: Optional column for text labels on bars.
            **kwargs: Additional arguments passed to px.bar.

        Returns:
            Plotly Figure object.
        """
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            color_discrete_sequence=color_discrete_sequence,
            orientation=orientation,
            text=text,
            **kwargs,
        )

        # Update bar text if provided
        if text:
            fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")

        # Hover template
        hover = self._format_hover_template(
            x_label=x, y_label=y, y_is_currency=y_is_currency, y_is_percent=y_is_percent
        )
        fig.update_traces(hovertemplate=hover)

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=xaxis_title or x,
            yaxis_title=yaxis_title or y,
            height=height,
        )

    def grouped_bar_chart(
        self,
        df,
        x: str,
        y: str,
        color: str,
        title: str | None = None,
        barmode: str = "group",
        height: int = 450,
        y_is_currency: bool = False,
        **kwargs,
    ) -> go.Figure:
        """Create a grouped bar chart."""
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            barmode=barmode,
            **kwargs,
        )

        hover = self._format_hover_template(
            x_label=x, y_label=y, y_is_currency=y_is_currency
        )
        fig.update_traces(hovertemplate=hover)

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=x,
            yaxis_title=y,
            height=height,
        )

    # -----------------------------------------------------------------------
    # Line Charts
    # -----------------------------------------------------------------------

    def line_chart(
        self,
        df,
        x: str,
        y: str,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str | None = None,
        color: str | None = None,
        markers: bool = True,
        height: int = 450,
        y_is_currency: bool = False,
        **kwargs,
    ) -> go.Figure:
        """Create a line chart.

        Args:
            df: DataFrame containing the data.
            x: Column name for x-axis.
            y: Column name for y-axis.
            title: Chart title.
            xaxis_title: X-axis label.
            yaxis_title: Y-axis label.
            color: Optional column to create multiple lines.
            markers: Show markers on data points.
            height: Chart height in pixels.
            y_is_currency: Format y-axis as INR in hover.
            **kwargs: Additional arguments passed to px.line.

        Returns:
            Plotly Figure object.
        """
        fig = px.line(
            df,
            x=x,
            y=y,
            color=color,
            markers=markers,
            **kwargs,
        )

        hover = self._format_hover_template(
            x_label=x, y_label=y, y_is_currency=y_is_currency
        )
        fig.update_traces(
            hovertemplate=hover, mode="lines+markers" if markers else "lines"
        )

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=xaxis_title or x,
            yaxis_title=yaxis_title or y,
            height=height,
        )

    # -----------------------------------------------------------------------
    # Heatmap (Correlation Matrix)
    # -----------------------------------------------------------------------

    def correlation_heatmap(
        self,
        corr_matrix,
        title: str | None = None,
        height: int = 500,
        width: int | None = None,
        highlight_pairs: list[tuple[str, str]] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a correlation matrix heatmap.

        Args:
            corr_matrix: Square correlation matrix (DataFrame or 2D array).
            title: Chart title.
            height: Chart height in pixels.
            width: Chart width in pixels.
            highlight_pairs: List of (row, col) pairs to annotate with values.
            **kwargs: Additional arguments passed to go.Heatmap.

        Returns:
            Plotly Figure object.
        """
        # Extract labels and values
        if hasattr(corr_matrix, "columns"):
            labels = list(corr_matrix.columns)
            z = corr_matrix.values
        else:
            labels = [f"V{i}" for i in range(len(corr_matrix))]
            z = corr_matrix

        fig = go.Figure(
            data=go.Heatmap(
                z=z,
                x=labels,
                y=labels,
                colorscale="RdBu_r",
                zmid=0,
                zmin=-1,
                zmax=1,
                text=[[f"{val:.3f}" for val in row] for row in z],
                texttemplate="%{text}",
                textfont={"size": 10, "color": "#F8FAFC"},
                hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>",
                colorbar=dict(
                    title=dict(text="Pearson r", font=dict(color="#94A3B8")),
                    tickfont=dict(color="#94A3B8"),
                ),
                **kwargs,
            )
        )

        fig.update_layout(
            title=title,
            height=height,
            width=width,
            template=self.default_template,
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(color="#94A3B8"),
            ),
            yaxis=dict(
                tickfont=dict(color="#94A3B8"),
            ),
        )

        return fig

    # -----------------------------------------------------------------------
    # Histogram / Distribution
    # -----------------------------------------------------------------------

    def histogram(
        self,
        df,
        x: str,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str = "Count",
        color: str | None = None,
        nbins: int = 30,
        opacity: float = 0.75,
        height: int = 450,
        marginal: str | None = "box",
        **kwargs,
    ) -> go.Figure:
        """Create a histogram with optional marginal plot."""
        fig = px.histogram(
            df,
            x=x,
            color=color,
            nbins=nbins,
            opacity=opacity,
            marginal=marginal,
            **kwargs,
        )

        fig.update_traces(
            hovertemplate=f"<b>{x}:</b> %{{x}}<br><b>Count:</b> %{{y}}<extra></extra>"
        )

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=xaxis_title or x,
            yaxis_title=yaxis_title,
            height=height,
        )

    def distribution_overlay(
        self,
        df,
        x: str,
        color: str,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str = "Density",
        histnorm: str = "probability density",
        height: int = 450,
        barmode: str = "overlay",
        opacity: float = 0.6,
        **kwargs,
    ) -> go.Figure:
        """Create overlaid histograms for comparing distributions."""
        fig = px.histogram(
            df,
            x=x,
            color=color,
            histnorm=histnorm,
            barmode=barmode,
            opacity=opacity,
            **kwargs,
        )

        fig.update_traces(
            hovertemplate=f"<b>{x}:</b> %{{x}}<br><b>Density:</b> %{{y:.4f}}<extra></extra>"
        )

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=xaxis_title or x,
            yaxis_title=yaxis_title,
            height=height,
        )

    # -----------------------------------------------------------------------
    # Scatter / Bubble
    # -----------------------------------------------------------------------

    def scatter_chart(
        self,
        df,
        x: str,
        y: str,
        title: str | None = None,
        xaxis_title: str | None = None,
        yaxis_title: str | None = None,
        color: str | None = None,
        size: str | None = None,
        hover_data: list[str] | None = None,
        height: int = 450,
        y_is_currency: bool = False,
        **kwargs,
    ) -> go.Figure:
        """Create a scatter plot."""
        fig = px.scatter(
            df,
            x=x,
            y=y,
            color=color,
            size=size,
            hover_data=hover_data,
            **kwargs,
        )

        hover = self._format_hover_template(
            x_label=x, y_label=y, y_is_currency=y_is_currency
        )
        fig.update_traces(hovertemplate=hover)

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=xaxis_title or x,
            yaxis_title=yaxis_title or y,
            height=height,
        )

    # -----------------------------------------------------------------------
    # Pie / Donut
    # -----------------------------------------------------------------------

    def pie_chart(
        self,
        df,
        values: str,
        names: str,
        title: str | None = None,
        hole: float = 0.0,
        height: int = 450,
        values_is_currency: bool = False,
        **kwargs,
    ) -> go.Figure:
        """Create a pie or donut chart."""
        fig = px.pie(
            df,
            values=values,
            names=names,
            hole=hole,
            **kwargs,
        )

        if values_is_currency:
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>Value: ₹%{value:,.2f}<br>Percent: %{percent}<extra></extra>",
                texttemplate="%{label}<br>%{percent}",
            )
        else:
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<br>Percent: %{percent}<extra></extra>",
                texttemplate="%{label}<br>%{percent}",
            )

        return self._apply_standard_layout(fig, title=title, height=height)

    # -----------------------------------------------------------------------
    # Box / Violin
    # -----------------------------------------------------------------------

    def box_chart(
        self,
        df,
        x: str | None,
        y: str,
        title: str | None = None,
        color: str | None = None,
        height: int = 450,
        y_is_currency: bool = False,
        **kwargs,
    ) -> go.Figure:
        """Create a box plot."""
        fig = px.box(
            df,
            x=x,
            y=y,
            color=color,
            **kwargs,
        )

        if y_is_currency:
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>Min: ₹%{y0:,.2f}<br>Q1: ₹%{y1:,.2f}<br>Median: ₹%{y2:,.2f}<br>Q3: ₹%{y3:,.2f}<br>Max: ₹%{y4:,.2f}<extra></extra>"
            )

        return self._apply_standard_layout(
            fig,
            title=title,
            xaxis_title=x,
            yaxis_title=y,
            height=height,
        )

    # -----------------------------------------------------------------------
    # Subplot Helper
    # -----------------------------------------------------------------------

    def create_subplot_grid(
        self,
        rows: int,
        cols: int,
        subplot_titles: list[str] | None = None,
        shared_xaxes: bool = False,
        shared_yaxes: bool = False,
        vertical_spacing: float = 0.12,
        horizontal_spacing: float = 0.08,
        height: int | None = None,
        width: int | None = None,
    ) -> go.Figure:
        """Create a subplot grid for multi-chart layouts."""
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            shared_xaxes=shared_xaxes,
            shared_yaxes=shared_yaxes,
            vertical_spacing=vertical_spacing,
            horizontal_spacing=horizontal_spacing,
        )

        # Apply dark template to the base figure
        fig.update_layout(template=self.default_template)

        if height:
            fig.update_layout(height=height)
        if width:
            fig.update_layout(width=width)

        return fig
