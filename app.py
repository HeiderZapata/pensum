import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, State
from dash.dependencies import Input, Output

app = Dash(__name__)

server = app.server

app.title = 'Pensum perfecto'

df = pd.read_excel("EA_PROGRAMACION_ACADEMICA_27MAY.xlsx", skiprows=1)

df['indice'] = df.index.tolist()
df['key'] = df['indice'].astype(str) + "a"

# primer df
sin_horario = df.copy()[df['Días'].isna()]

df = df.copy()[df['Días'].isna() == False]

df['Días'] = df['Días'].str.split(",")
df['lendias'] = df['Días'].apply(lambda x: len(x))

# Duplicar filas que cumplan cierta condicion
lista_df = []

for ndias in df['lendias'].unique().tolist():
    if ndias == 1:
        marca = df['lendias'] == ndias
        df1 = df.copy()[marca]
        lista_df.append(df1)
    else:
        marca = df['lendias'] == ndias
        df_temp = df.copy()[marca]
        df_temp2 = pd.concat([df_temp] * ndias, ignore_index=True)
        lista_df.append(df_temp2)

nuevo = pd.concat(lista_df).sort_values(by=['key']).reset_index(drop=True)

lista_df = []
for i in nuevo['key'].unique().tolist():
    temp = nuevo.copy()[nuevo['key'] == i].reset_index()
    temp['Días'] = temp['Días'][0]
    lista_df.append(temp)
final = pd.concat(lista_df + [sin_horario]).reset_index(drop=True)

usecols = ['Grado_Academico', 'Código Catálogo', 'Número de Clase', 'Hora Inicio', 'Hora Fin', 'Días',
           'Nom Estado Clase',
           'Aula Asignada', 'Fecha_Ini_Mod_Reunión', 'Fecha_Fin_Mod_Reunión']
# final = final.copy()[usecols+['key','lendias']]

final.Días = final.Días.str.strip()

pa_origin = final.copy()[usecols + ['key', 'lendias']]

# Rename some columns of the original DF
pa_origin.rename(columns={'Grado_Academico': 'Grado_Acad', 'Código Catálogo': 'Catálogo', 'Número de Clase': 'Clase',
                          'Fecha_Ini_Mod_Reunión': 'Fecha Ini', 'Fecha_Fin_Mod_Reunión': 'Fecha Fin',
                          'Hora Inicio': 'Hora Ini', 'Días': 'Día', 'Aula Asignada': 'Aula',
                          'Nom Estado Clase': 'Estado Clase'}, inplace=True)

# Show which items Grado_Acad column has and rename it
pa_origin['Grado_Acad'] = pa_origin['Grado_Acad'].str.replace('PREG - Pregrado', 'Pregrado').str.replace(
    'DOCT - Doctorado', 'Doctorado').str.replace('ESPE - Especialización', 'Especialización').str.replace(
    'MSTR - Maestría', 'Maestría')

# Make a copy of the Academic programation Df and create a new column "Hora_ini-Hora_fin"
pa = pa_origin.copy()
# filter 'pregrado'
pa = pa[pa['Grado_Acad'] == 'Pregrado']
# filter 'Active' clases
#pa = pa[pa['Estado Clase'] == 'Activo']
# create "Hora_ini - Hora_fin" column
pa['Hora_ini - Hora_fin'] = pa['Hora Ini'] + ' - ' + pa['Hora Fin']

# Read the layout Demanda made by Bibiana
demanda = pd.read_excel('EA_PLAN_ACADEMICO.xlsx', sheet_name='planes_oblig', index_col='Catálogo',
                        dtype={'Nro Semestre': str})

# Create a copy of this Demand DF
demanda_cp = demanda.copy()
demanda_cp = demanda.drop('c1', axis=1)
demanda_cp = demanda.drop('dpto', axis=1)

# Create a column called 'plan-nivel' in demanda_cp dataframe
demanda_cp['plan-nivel'] = demanda_cp['Plan Acad'] + '-' + demanda_cp['Nro Semestre']
# demanda_cp.head()

app.layout = html.Div([

    html.Div(children=[
        html.Img(
            src='data:image/png;base64,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')
    ]),

    html.H1(children='Validador pénsum perfecto Admisiones y Registro',
            style={'font-family': 'arial', 'textAlign': 'center', 'color': 'black'}),

    html.Br(),

    html.Div([
        html.H3('Digite el código del catálogo que quiere programar:  ',
                style={'font-family': 'arial', 'color': 'black'}),
        html.Div(dcc.Input(id='input-on-submit', type='text', placeholder='En mayúscula', style={'height': '30px'})),
        html.Button('Submit', id='submit-val', n_clicks=0, style={'height': '30px'}),
        html.Div(id='container-button-basic',
                 children='')

        # html.Label('Digite el catálogo que quiere cambiar de horario: '),
        # html.Br(),
        # html.Div(dcc.Input(id="my_catalog", type="text", placeholder="En Mayusculass"))]),
        # html.Br(),

    ],
        # this line centers the Input
        style=dict(display='flex', justifyContent='center')),

    # html.H2(children='''
    # Los cajones con número distinto a cero (0) son horarios donde NO se puede programar la materia

    #    ''', style={'textAlign': 'center', 'color': 'black'}),

    # html.P('my_output'),

    html.Br(),

    html.Div([dcc.Graph(id='my_graph', figure={})]),

])


@app.callback(
    # Output('container-button-basic', 'children'),
    Output(component_id='my_graph', component_property='figure'),
    # Output(component_id='my_output', component_property='children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value')
    # Output(component_id='my_graph', component_property='figure'),
    # Output(component_id='output_container', component_property='children')],
    # Input(component_id='my_catalog', component_property='value')
)
# def update_output(n_clicks,value):
#   return f'Comparando horario de {value} Vs {len(SEM_DEPURADO)} materias del mismo plan y que tienen menos de 6 grupos'

def update_graph(n_clicks, value):
    # This is the information of the Course selected
    datos_asignatura = demanda_cp.loc[[value], ['nombre_materia', 'plan-nivel']]
    # datos_asignatura ¡¡¡¡PRINT THIS LATER!!!!

    # Create a list with the plans-nivels of the course given above
    planes_asignatura = [x for x in datos_asignatura['plan-nivel'] if str(x) != 'nan']
    # planes_asignatura ¡¡¡¡PRINT THIS LATER!!!!

    # Create a DF with all the plans and data of the given course
    all_plans = pd.DataFrame()
    for x in range(len(planes_asignatura)):
        all_plans = all_plans.append(demanda_cp[demanda_cp['plan-nivel'] == planes_asignatura[x]])

    # Drop 99 levels
    # indexesNivel_99 = all_plans[all_plans['nivel']=='99'].index
    # all_plans.drop(indexesNivel_99,inplace=True)
    # indexesNivel_99 ¡¡¡¡PRINT THIS LATER!!!!

    # These are the courses to avoid crashes between them
    no_cruce_list = all_plans.index.to_list()

    # NEW SET
    Set_no_cruce_list = set(no_cruce_list)
    List_no_cruce_list = list(Set_no_cruce_list)
    # NEW SET
    # no_cruce_list ¡¡¡¡PRINT THIS LATER!!!!

    # this is the Acad prog of the course given above
    horario_de_la_materia = pa[pa['Catálogo'] == value]  # .nunique()
    # horario_de_la_materia ¡¡¡¡PRINT THIS LATER!!!!

    # Num groups of the GIVEN course
    numGrupMat = horario_de_la_materia['Clase'].nunique()
    # print(f'la materia {asignatura} tiene {numGrupMat} clases') ¡¡¡¡PRINT THIS LATER!!!!

    # Get the curses with 6 or less clases in the semester of the course given
    SEM_DEPURADO = []
    i = 0
    for mat in List_no_cruce_list:
        pa_materiaXposi = pa[pa['Catálogo'] == List_no_cruce_list[i]]
        numGrupMateriaXposi = pa_materiaXposi['Clase'].nunique()
        if numGrupMateriaXposi >= 1 and numGrupMateriaXposi <= 6:
            SEM_DEPURADO.append(mat)
        i += 1

    lenSemDep = len(SEM_DEPURADO)  # print lenght depurated semester
    # print(SEM_DEPURADO)  ¡¡¡¡PRINT THIS LATER!!!!
    # print(lenSemDep)
    i = 0
    # marc=['1','2','3','4']
    all_mat = pd.DataFrame()  # create an empty df
    for MAT in range(lenSemDep):
        all_mat = all_mat.append(pa[pa['Catálogo'] == SEM_DEPURADO[MAT]], ignore_index=True)

    # Numerar los días.
    conditions = [all_mat['Día'] == 'Lunes',
                  all_mat['Día'] == 'Martes',
                  all_mat['Día'] == 'Miercoles',
                  all_mat['Día'] == 'Jueves',
                  all_mat['Día'] == 'Viernes',
                  all_mat['Día'] == 'Sábado',
                  all_mat['Día'] == 'Domingo']

    choices = ['1', '2', '3', '4', '5', '6', '7']

    all_mat['num_dia'] = np.select(conditions, choices, default=np.nan)

    all_mat['numYdia'] = all_mat['num_dia'] + '-' + all_mat['Día']

    ctab = pd.crosstab(index=all_mat["Hora_ini - Hora_fin"], columns=all_mat["numYdia"])
    fig = px.imshow(ctab, title=value, labels={'x': 'Día', 'y': 'Hora ini - Hora fin'},
                    aspect='auto', text_auto=True, color_continuous_scale='portland', width=900, height=1100)
    # fig = go.Figure(data=go.Heatmap(ctab))
    fig.update_xaxes(side="top")
    fig.update_layout(coloraxis_showscale=False)

    return fig


if __name__ == '__main__':
    app.run_server(debug=False)