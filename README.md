# 🔋 Smart Home RL Optimizer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

Тут мы интерактивно исследуем **Марковский процесс принятия решений** и решение задачи при помощи динамического программирования. 

## Мат модель

Решаем уравнение оптимальности Беллмана

$$V(s) \leftarrow \max_a \sum_{s', r} p(s', r | s, a) [r + \gamma V(s')]$$