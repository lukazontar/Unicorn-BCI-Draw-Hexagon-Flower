# Unicorn BCI: Draw Hexagon Flower

**Description:** Repository for Unicorn BCI app to draw a hexagon flower as part of
the [Speculum Artium Festival 2023](https://speculumartium.si/wp21/?lang=en). In this exhibition piece, you can be part
of a collaborative digital art project, where participants interact with the hexagon flower to create a unique digital
masterpiece.

## Repository Structure

This repository contains folders:

* ```api/``` - contains the backend code for the app (data acquisition from BCI and data visualization).
* ```art/``` - contains the version dumps of digital art that was created as part of the project.
* ```data/``` - contains the brain computer interface data and the current state of the board.
* ```docs/``` - contains additional documentation of the repository, project and BCI usage.
* ```ui/``` - contains the frontend code for the app (visualization of the hexagon flower along with the admin console).

*Link to Original Idea Article*: [here](./docs/report/Art_project_using_brain_interface_to_draw_a_hexagon_flower.pdf)
*Link to BCI User Manual*: [here](./docs/UnicornSuite-UserManual.pdf)
*Link to Project Usage Instructions*: [here](./docs/User Instructions - EN.pdf)

Unicorn Speller Board can be found in `./docs/unicorn_speller_board/SpellerBoard.ibc` file.

# Computer specifications :computer:

Here are the specifications of the computer that was used when developing:

- PyCharm Professional
- Python 3.8.10

# Setting up the environment :snake:

To reproduce results, you will need to fork this repository and install Python dependencies using `virtualenv`
and `pip`.

We used PyCharm to create virtual environment. Alternatively, find instructions to do it via your
terminal [here](https://docs.python.org/3/library/venv.html).

Next, use `pip` to install requirements from `requirements.txt`:

```
pip install -r requirements.txt
```

Now your environment is ready to go.:partying_face: :clinking_glasses:
