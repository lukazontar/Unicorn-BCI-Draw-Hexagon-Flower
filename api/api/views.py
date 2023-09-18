import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from requests import RequestException, Request


def map_personal_id_to_ix_triangle(personal_id: str,
                                   board_state: dict):
    """
    From personal ID generates an index of triangle that will be colored.
    It is generated as the modulo division of sum of personal ID integers
    by the total number of triangles.

    :param personal_id: Personal ID parameter.
    :param board_state: Board state dictionary.
    :return: Index of triangle that will be colored and equation string how
    this index is calculated.
    """
    list_int_personal_id = list(
        map(lambda x: int(x), personal_id)
    )
    list_str_personal_id = list(personal_id)

    # Total number of triangles .
    total_triangles = len(board_state['triangles'])
    # Calculate the index of triangle that will be colored.
    result = sum(list_int_personal_id) % total_triangles

    # Generate the equation string that will be shown to user.
    equation = f"({'+'.join(list_str_personal_id)}) % {total_triangles} = {result}"

    return str(result), equation


def save_board_state(board_state: dict):
    """
    Saves the current state of hexagon flower board.

    :param board_state: Board state dictionary.
    :return: None.
    """

    # Serializing json.
    json_object = json.dumps(board_state, indent=4)

    # Writing to sample.json.
    with open(f"../data/current_state.json", "w+") as outfile:
        outfile.write(json_object)


def init_board_state(n_triangles_bottom: int):
    """
    Generates an entirely new, cleared board state.

    :param n_triangles_bottom: Number of equilateral triangles in the bottom row of the bigger equilateral triangle.
    :return: Board state dictionary.
    """
    state = {
        'n_triangles_bottom': n_triangles_bottom,
        'triangles': {},
        'log_activity': []
    }

    n_triangles_total = sum(range(n_triangles_bottom + 1)) * 2 - n_triangles_bottom
    for i in range(n_triangles_total):
        state['triangles'][str(i)] = {
            'color': 'white',
            'index': i
        }
    return state


def init_canvas(request: Request):
    """
    API request returning the current version board state. If none exists or number of triangles changed, new board state is created.
    :param request: HTML request data.
    :return: Board state JSON dictionary.
    """
    n_triangles_bottom = int(request.GET['nTrianglesBottom'])
    try:
        try:
            # Try to open the current state of board state JSON.
            with open('../data/current_state.json', 'r', encoding='utf-8') as current_state_file:
                board_state = json.load(current_state_file)
            # If number of triangles changed, new board state is created.
            if n_triangles_bottom != board_state['n_triangles_bottom']:
                # Initialize board state.
                board_state = init_board_state(n_triangles_bottom=n_triangles_bottom)
        except Exception:
            # If current board state does not exist, new board state is created.
            board_state = init_board_state(n_triangles_bottom=n_triangles_bottom)

        # Save board state.
        save_board_state(board_state)
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}))
    # Return board state.
    return HttpResponse(json.dumps(board_state))


def color_triangle(request: Request):
    """
    From a personal ID generates an index of a triangle that will be colored with given color. Modified board state JSON is returned.

    :param request: HTML request data.
    :return: Board state JSON dictionary.
    """
    # Retrieve parameters personal ID and color.
    personal_id = str(request.GET['personalId'])
    if not personal_id.isdigit() or personal_id is None:
        return HttpResponse(json.dumps({
            'error': "Personal ID contains non-digit characters or is the value missing. Please, fix the personal IDs so that it only contains digits."}))

    if personal_id is None:
        return HttpResponse(json.dumps({
            'error': "Color is missing. Please, fill the color field."}))

    color = str(request.GET['color'])

    try:
        # Try to open the current state of board state JSON.
        with open('../data/current_state.json', 'r', encoding='utf-8') as current_state_file:
            # Load JSON.
            board_state = json.load(current_state_file)

            # From personal ID generate an index of triangle to be colored.
            ix_triangle, equation = map_personal_id_to_ix_triangle(personal_id=personal_id,
                                                                   board_state=board_state)

            # Modify board state according to change.
            board_state['triangles'][ix_triangle]['color'] = color

            # Save last equation and index triangle to emphasize last colored triangle
            # and the last equation that will be shown to users.
            board_state['last_ix_triangle_colored'] = ix_triangle
            board_state['last_equation'] = equation
            # Log activity.
            board_state['log_activity'].append(
                f'Triangle with index <b>{ix_triangle}</b> was colored with <b>{color}</b> color.'
            )
    except Exception:
        # Throw exception that board state could not load.
        return HttpResponse(json.dumps({
            'error': 'Current Hexagon flower board state could not load. Delete data/current_state.json file and restart server.'}))

    # Save board state.
    save_board_state(board_state)

    # Set 'confirm' property in brain interface data to False
    with open('../data/brain_interface_data.json', 'r+') as file:
        # Read state of brain interface data.
        data = json.load(file)

        data['confirm'] = False

        # Writing to json.
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    # Return modified board state.
    return HttpResponse(json.dumps(board_state))


def remove_ux_svg_elems(svg_data: str):
    """
    Takes the string of SVG elements and remove texts and makes all
    the triangles of equal stroke width.
    This way we remove features used for better user experience.

    :param svg_data: SVG string.
    """
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    # Parse SVG
    tree = ET.ElementTree(ET.fromstring(svg_data))
    root = tree.getroot()
    # Go through all the SVG groups
    for g in root.getchildren():
        # Go through all the children.
        for child in g.getchildren():
            child_tag = child.tag.replace('{http://www.w3.org/2000/svg}', '')
            # Remove texts - triangle indices used for better UX
            if child_tag == 'text':
                g.remove(child)
            # Set all triangle stroke widths to 1 (to remove the emphasis on lastly colored triangle)
            if child_tag == 'polygon':
                child.attrib['stroke-width'] = '1'
    return ET.tostring(root)


@csrf_exempt
def save_canvas(request: Request):
    """
    Saves the image (.png) of current state of the generated hexagon flower art.

    :param request: HTML request data containing the base64 image data.
    """
    timestamp_str = datetime.now().strftime('%m-%d-%Y, %H-%M-%S')
    try:
        data = json.loads(request.body.decode('utf-8'))['data']
        decoded_data = base64.b64decode(data.replace("data:image/svg+xml;base64,", ""))
        svg_file_name = f"../art/Art {timestamp_str}.svg"

        svg_data = remove_ux_svg_elems(svg_data=decoded_data)
        with open(svg_file_name, 'w+', encoding='utf-8') as svg_file:
            svg_file.write(svg_data.decode('utf-8'))
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}))

    # Also save board state to an archive file
    try:
        # Try to open the current state of board state JSON.
        with open('../data/current_state.json', 'r', encoding='utf-8') as current_state_file:
            # Load JSON.
            data = json.load(current_state_file)
            archive_board_state_file_name = f"../art/Board state {timestamp_str}.json"
            with open(archive_board_state_file_name, 'w+', encoding='utf-8') as archive_board_state_file:
                archive_board_state_file.write(json.dumps(data, indent=4))
    except:
        # Throw exception that brain interface data does not exist.
        raise RequestException(
            'Board state data does not exist.')

    # Return success.
    return HttpResponse(json.dumps({'success': 'true'}))


def clear_canvas(request: Request):
    """
    Returns clear board state.

    :param request: HTML request data.
    :return: Board state JSON dictionary.
    """
    n_triangles_bottom = int(request.GET['nTrianglesBottom'])

    # Initialize board state.
    board_state = init_board_state(n_triangles_bottom=n_triangles_bottom)

    # Save clear board state.
    save_board_state(board_state)

    # Return modified board state.
    return HttpResponse(json.dumps(board_state))


def read_brain_interface_data(request: Request):
    """
    Read brain computer interface data.

    :param request: HTML request data.
    :return: Current state of brain computer interface data.
    """
    try:
        # Try to open the current state of board state JSON.
        with open('../data/brain_interface_data.json', 'r', encoding='utf-8') as brain_interface_data_file:
            # Load JSON.
            data = json.load(brain_interface_data_file)

            # Return brain interface data.
            return HttpResponse(json.dumps(data))
    except:
        # Throw exception that brain interface data does not exist.
        raise RequestException(
            'Brain interface data does not exist.')


def read_board_state_data(request: Request):
    """
    Read board state data.

    :param request: HTML request data.
    :return: Current state of brain computer interface data.
    """
    try:
        # Try to open the current state of board state JSON.
        with open('../data/current_state.json', 'r', encoding='utf-8') as current_state_file:
            # Load JSON.
            data = json.load(current_state_file)

            # Return brain interface data.
            return HttpResponse(json.dumps(data))
    except:
        # Throw exception that brain interface data does not exist.
        raise RequestException(
            'Brain interface data does not exist.')


def clear_single_input(request: Request):
    """
    Clear single input in brain computer interface data from personal ID.

    :param request: HTML request data.
    :return: Empty response.
    """
    # Save new item to brain interface data.
    with open('../data/brain_interface_data.json', 'r+') as file:
        # Read state of brain interface data.
        data = json.load(file)

        data['personal_id'] = data['personal_id'][:-1]

        # Writing to json.
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    # Return brain interface data.
    return HttpResponse(json.dumps(data))


def clear_entire_input(request: Request):
    """
    Clear entire input in brain computer interface data from personal ID.

    :param request: HTML request data.
    :return: Empty response.
    """
    # Save new item to brain interface data.
    with open('../data/brain_interface_data.json', 'r+') as file:
        # Read state of brain interface data.
        data = json.load(file)

        data['personal_id'] = ""

        # Writing to json.
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    # Return brain interface data.
    return HttpResponse(json.dumps(data))


def clear_color(request: Request):
    """
    Clear single input in brain computer interface data from personal ID.

    :param request: HTML request data.
    :return: Empty response.
    """
    # Save new item to brain interface data.
    with open('../data/brain_interface_data.json', 'r+') as file:
        # Read state of brain interface data.
        data = json.load(file)

        # Default value - red color - is set
        data['color'] = "red"

        # Writing to json.
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    # Return brain interface data.
    return HttpResponse(json.dumps(data))
