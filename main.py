# main.py

import numpy as np
import streamlit as st

from core.env import SmartHomeEnv
from core.solver import ValIterSolver

from ui.styles import CUSTOM_CSS
from ui.sidebar import render_sidebar
from ui.pricing import build_prices, ACTIONS
from ui.simulation import run_simulation
from ui.plots import (
    make_prices_chart,
    make_policy_heatmap,
    make_value_heatmap,
    make_simulation_chart,
    make_balance_chart,
)
from ui.math_tab import render_math_tab


# ============================================================
# страница
# ============================================================
st.set_page_config(
    page_title="Умный дом",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Считаем оптимальную стратегию...")
def compute_policy(max_battery: int, prob_sun: float, prices_tuple: tuple):
    env = SmartHomeEnv(
        prices=np.array(prices_tuple),
        actions=list(ACTIONS),
        max_battery=max_battery,
        prob_sun=prob_sun,
    )
    V, Policy = ValIterSolver(env).solve()
    return V, Policy


cfg = render_sidebar()

prices = build_prices(cfg.night_price, cfg.day_price, cfg.peak_price)
V, Policy = compute_policy(cfg.max_battery, cfg.prob_sun, tuple(prices.tolist()))

env = SmartHomeEnv(
    prices=prices,
    actions=list(ACTIONS),
    max_battery=cfg.max_battery,
    prob_sun=cfg.prob_sun,
)


# ============================================================
# вкладки
# ============================================================
tab_main, tab_math = st.tabs(["⚡ Стратегия и симуляция", "📖 Как это работает"])

# ================================================================
# Вкладка 1: стратегия и симуляция
# ================================================================
with tab_main:
    st.markdown(
        """
        <div class="hero">
            <h1>Умный домик</h1>
            <p>
                Представьте, что у вас есть дом, солнечные панели и батарея.
                Электричество стоит по-разному в течение дня:
                ночью копейки, в часы пик дороже. Алгоритм сам разбирается, когда покупать,
                когда продавать, а когда просто ничего не делать. Поиграйтесь с настройками
                слева - стратегия пересчитается под них.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔋 Батарея", f"{cfg.max_battery} кВт·ч")
    with c2:
        st.metric("☀️ Шанс солнца днём", f"{cfg.prob_sun:.0%}")
    with c3:
        st.metric("⚡ Заряд с утра", f"{cfg.start_battery} кВт·ч")

    with st.expander("💡 Гайд к графикам", expanded=False):
        st.markdown(
            """
            - На карте стратегии: горизонталь - час суток, вертикаль - текущий заряд батареи.
              Цвет клетки = совет алгоритма для этой ситуации.
            - Красные оттенки - продаём, синие - покупаем, серый - не трогаем батарею.
            - На карте ценности ниже красные клетки - выгодные ситуации, светлее - так себе.
              Это про то, насколько выгодна нам эта ситуация.
            """
        )

    st.markdown("---")

    left, right = st.columns([0.9, 1.3])

    with left:
        st.subheader("💸 Что почём в течение суток")
        st.caption("Ночью копейки, вечером (17-20) самый пик.")
        st.plotly_chart(make_prices_chart(env.prices), use_container_width=True)

    with right:
        st.subheader("🧠 Что советует делать алгоритм")
        st.caption("Каждая клетка - совет для конкретной ситуации.")
        st.plotly_chart(
            make_policy_heatmap(Policy, cfg.max_battery),
            use_container_width=True,
        )
        st.markdown(
            '<div class="small-note">🔴 продаём, 🔵 покупаем, серый - сидим ровно.</div>',
            unsafe_allow_html=True,
        )

    st.subheader("📈 Насколько хороша каждая ситуация")
    st.caption(
        "Чем краснее клетка, тем лучше в ней оказаться. Тут учтены не только сегодняшние "
        "деньги, но и все будущие возможности с дисконтом. (т.е. мат ожид по сути)"
    )
    st.plotly_chart(
        make_value_heatmap(V, cfg.max_battery),
        use_container_width=True,
    )

    st.markdown("---")

    st.subheader("🎲 Что получится за сутки")
    st.caption(
        f"Запускаем стратегию на 24 часа вперёд. С утра в батарее {cfg.start_battery} кВт·ч, "
        f"солнце выпадает случайно с шансом {cfg.prob_sun:.0%}."
    )

    sim = run_simulation(env, Policy, cfg.start_battery)

    col_sim_left, col_sim_right = st.columns([1.6, 1])
    with col_sim_left:
        st.plotly_chart(make_simulation_chart(sim), use_container_width=True)
    with col_sim_right:
        st.plotly_chart(make_balance_chart(sim), use_container_width=True)

    m1, m2 = st.columns(2)
    with m1:
        st.metric("💰 Баланс в конце", f"{sim.final_cash:+.1f} у.е.")
    with m2:
        st.metric("🔋 Заряд в конце", f"{sim.final_battery} кВт·ч")


# ================================================================
# Вкладка 2: математика
# ================================================================
with tab_math:
    render_math_tab()
