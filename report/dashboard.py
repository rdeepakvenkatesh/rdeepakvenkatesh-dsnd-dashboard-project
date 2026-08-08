from fasthtml.common import *
import matplotlib.pyplot as plt

# Import from the installed employee_events package
from employee_events import QueryBase, Employee, Team

# Import model-loading utility from report/utils.py
from utils import load_model

from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable,
)

from combined_components import FormGroup, CombinedComponent


class ReportDropdown(Dropdown):
    """Dropdown containing employee or team names and IDs."""

    def build_component(self, entity_id, model):
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


class Header(BaseComponent):
    """Dynamic dashboard title."""

    def build_component(self, entity_id, model):
        return H1(f"{model.name.title()} Performance")


class LineChart(MatplotlibViz):
    """Cumulative positive and negative employee events."""

    def visualization(self, entity_id, model):
        event_data = model.event_counts(entity_id)

        event_data = event_data.fillna(0)
        event_data = event_data.set_index("event_date")
        event_data = event_data.sort_index()
        event_data = event_data.cumsum()

        event_data.columns = ["Positive", "Negative"]

        fig, ax = plt.subplots()

        if event_data.empty:
            ax.set_title("No event data available")
            ax.axis("off")
        else:
            event_data.plot(ax=ax)

        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black",
        )

        ax.set_title("Cumulative Performance Events")
        ax.set_xlabel("Date")
        ax.set_ylabel("Event Count")


class BarChart(MatplotlibViz):
    """Machine-learning recruitment-risk visualization."""

    predictor = load_model()

    def visualization(self, entity_id, model):
        model_data = model.model_data(entity_id)

        probabilities = self.predictor.predict_proba(model_data)
        probabilities = probabilities[:, 1]

        if model.name == "team":
            pred = probabilities.mean()
        else:
            pred = probabilities[0]

        # Optional rubric enhancement: risk color scale
        if pred < 0.33:
            bar_color = "green"
        elif pred < 0.67:
            bar_color = "orange"
        else:
            bar_color = "red"

        fig, ax = plt.subplots()

        ax.barh(
            [""],
            [pred],
            color=bar_color,
        )

        ax.set_xlim(0, 1)
        ax.set_xlabel("Probability")
        ax.set_title(
            "Predicted Recruitment Risk",
            fontsize=20,
        )

        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black",
        )


class Visualizations(CombinedComponent):
    """Container for the two dashboard visualizations."""

    children = [
        LineChart(),
        BarChart(),
    ]

    outer_div_type = Div(cls="grid")


class NotesTable(DataTable):
    """Notes associated with the selected employee or team."""

    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):
    """Employee/team report filters."""

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector",
        ),
        ReportDropdown(
            id="selector",
            name="user-selection",
        ),
    ]


class Report(CombinedComponent):
    """Complete dashboard report."""

    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
    ]


app, rt = fast_app()

report = Report()


@rt("/")
def get():
    return report(1, Employee())


@rt("/employee/{id:str}")
def employee(id: str):
    return report(id, Employee())


@rt("/team/{id:str}")
def team(id: str):
    return report(id, Team())


# Keep the routes below unchanged.
@app.get("/update_dropdown{r}")
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]

    print("PARAM", r.query_params["profile_type"])

    if r.query_params["profile_type"] == "Team":
        return dropdown(None, Team())

    elif r.query_params["profile_type"] == "Employee":
        return dropdown(None, Employee())


@app.post("/update_data")
async def update_data(r):
    from fasthtml.common import RedirectResponse

    data = await r.form()

    profile_type = data._dict["profile_type"]
    entity_id = data._dict["user-selection"]

    print(
        "PROFILE:",
        profile_type,
        "ENTITY:",
        entity_id,
    )

    if profile_type == "Employee":
        return RedirectResponse(
            f"/employee/{entity_id}",
            status_code=303,
        )

    elif profile_type == "Team":
        return RedirectResponse(
            f"/team/{entity_id}",
            status_code=303,
        )


serve()