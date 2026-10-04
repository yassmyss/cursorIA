"""Optional UI checks. Run: python eval/smoke_ui.py after installing requirements."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
assert not app.exception
app.text_input[0].set_value('¿Dónde se guardan las reglas de proyecto .mdc?')
next(b for b in app.button if b.label == 'Consultar').click().run()
assert not app.exception and len(app.expander) > 1
app.text_input[0].set_value('')
next(b for b in app.button if b.label == 'Consultar').click().run()
assert not app.exception and len(app.warning) > 0
print('UI: inicio, consulta con fuentes y validación de entrada OK')
