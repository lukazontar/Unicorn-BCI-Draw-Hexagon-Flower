from django.urls import path

from . import views

urlpatterns = [
    path('initCanvas', views.init_canvas, name='initCanvas'),
    path('colorTriangle', views.color_triangle, name='colorTriangle'),
    path('saveCanvas', views.save_canvas, name='saveCanvas'),
    path('clearCanvas', views.clear_canvas, name='clearCanvas'),
    path('readBrainInterfaceData', views.read_brain_interface_data, name='readBrainInterfaceData'),
    path('readBoardStateData', views.read_board_state_data, name='readBoardStateData'),
    path('clearSingleInput', views.clear_single_input, name='clearSingleInput'),
    path('clearEntireInput', views.clear_entire_input, name='clearEntireInput'),
    path('clearColor', views.clear_color, name='clearColor')
]
