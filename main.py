import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from env import SmartHomeEnv
from solver import ValIterSolver

# ============================================================
# страница
# ============================================================
st.set_page_config(
    page_title="Умный дом",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# тёмная тема
# ============================================================
st.markdown(
    """
    <style>
    .stApp { background-color: #0b1220; }
    .block-container { padding-top: 1.4rem; max-width: 1340px; }

    .hero {
        background-color: #1a2236;
        border: 1px solid #2a334d;
        border-radius: 18px;
        padding: 1.7rem 1.9rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .hero h1 { color: #f1f5f9; margin-bottom: 0.6rem; }
    .hero p { color: #cbd5e1; line-height: 1.65; font-size: 1.02rem; margin: 0; }

    div[data-testid="stExpander"] {
        background-color: #1a2236;
        border: 1px solid #2a334d;
        border-radius: 14px;
    }
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] li { color: #cbd5e1; }

    .small-note { font-size: 0.92rem; color: #8b9bb4; }

    div[data-testid="stMetric"] { background: transparent; border: none; padding: 0; }
    div[data-testid="stMetric"] label { color: #8b9bb4 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f1f5f9 !important; }

    [data-testid="stSidebar"] { background-color: #161e30; }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    .stButton button {
        background-color: #3b82f6; color: white;
        border: none; border-radius: 10px;
    }

    div[data-testid="stTabs"] button {
        color: #cbd5e1; background-color: transparent; border: none;
        font-size: 1.05rem; font-weight: 500;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #3b82f6; color: #f1f5f9;
    }

    code {
        background-color: #2a334d; padding: 2px 6px;
        border-radius: 6px; color: #fbbf24;
    }
    a { color: #60a5fa; }

    h1, h2, h3, h4 { color: #f1f5f9; }

    /* блок-формулы: подсветка, чтобы выделялись в длинных текстах */
    .katex-display {
        margin: 1.2rem 0 !important;
        padding: 0.9rem 1rem;
        background-color: rgba(59,130,246,0.07);
        border-left: 3px solid #3b82f6;
        border-radius: 6px;
        overflow-x: auto;
    }
    .katex { color: #f1f5f9 !important; font-size: 1.08em; }

    /* инфо/успех/ворнинг блоки темнее */
    div[data-testid="stAlert"] {
        background-color: #1a2236 !important;
        border: 1px solid #2a334d;
        border-radius: 12px;
    }
    div[data-testid="stAlert"] * { color: #cbd5e1 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# вычисления (кеш)
# ============================================================
@st.cache_data(show_spinner="Считаем оптимальную стратегию...")
def compute_policy(max_battery: int, prob_sun: float):
    prices = np.array([5] * 7 + [15] * 10 + [50] * 4 + [5] * 3)
    actions = [-2, -1, 0, 1, 2]

    env = SmartHomeEnv(
        prices=prices,
        actions=actions,
        max_battery=max_battery,
        prob_sun=prob_sun,
    )
    solver = ValIterSolver(env)
    V, Policy = solver.solve()
    return V, Policy, env


# ============================================================
# сайдбар
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Настройки дома")
    st.markdown(
        '<p class="small-note">Покрутите ползунки и посмотрите, '
        "как меняется поведение алгоритма.</p>",
        unsafe_allow_html=True,
    )

    max_battery = st.slider(
        "Размер батареи, кВт·ч",
        min_value=2,
        max_value=20,
        value=10,
        step=1,
        help="Сколько энергии помещается в батарее.",
    )
    prob_sun = st.slider(
        "☀️ Как часто бывает солнце",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Шанс, что в светлый час панели дадут электричество.",
    )
    start_battery = st.slider(
        "Заряд батареи с утра, кВт·ч",
        min_value=0,
        max_value=max_battery,
        value=2,
        step=1,
        help="С чего стартуем при моделировании суток.",
    )

    st.markdown("---")
    st.markdown(
        """
        **Что умеет алгоритм каждый час:**
        - **-2, -1** - продать энергию в сеть
        - **0** - ничего не трогать
        - **+1, +2** - купить и зарядить батарею
        """
    )
    st.markdown(
        '<p class="small-note">Дом постоянно потребляет 1 кВт в час. '
        "Днём (с 8 до 18) панели иногда подкидывают +2 кВт.</p>",
        unsafe_allow_html=True,
    )

# ============================================================
# данные
# ============================================================
V, Policy, env = compute_policy(max_battery, prob_sun)

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
        st.metric("🔋 Батарея", f"{max_battery} кВт·ч")
    with c2:
        st.metric("☀️ Шанс солнца днём", f"{prob_sun:.0%}")
    with c3:
        st.metric("⚡ Заряд с утра", f"{start_battery} кВт·ч")

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
        st.caption("Ночью копейки, вечером (16-19) самый пик.")

        fig_prices = px.bar(
            x=list(range(24)),
            y=env.prices,
            labels={"x": "Час", "y": "Цена за кВт·ч"},
            text=env.prices,
        )
        fig_prices.update_traces(
            marker_color="#3b82f6",
            textposition="outside",
            textfont_size=14,
        )
        fig_prices.update_layout(
            template="plotly_dark",
            height=420,
            margin=dict(l=16, r=16, t=30, b=16),
            showlegend=False,
            xaxis=dict(tickmode="linear", dtick=1, title_font_size=14),
            yaxis=dict(range=[0, max(env.prices) * 1.2], title_font_size=14),
            paper_bgcolor="#1a2236",
            plot_bgcolor="#1a2236",
        )
        st.plotly_chart(fig_prices, use_container_width=True)

    with right:
        st.subheader("🧠 Что советует делать алгоритм")
        st.caption("Каждая клетка - совет для конкретной ситуации.")

        heatmap = go.Heatmap(
            z=Policy.T,
            x=list(range(24)),
            y=list(range(max_battery + 1)),
            colorscale=[
                [0.0, "#b91c1c"],
                [0.25, "#ef4444"],
                [0.5, "#475569"],
                [0.75, "#3b82f6"],
                [1.0, "#1d4ed8"],
            ],
            zmin=-2,
            zmax=2,
            showscale=True,
            colorbar=dict(
                tickvals=[-2, -1, 0, 1, 2],
                ticktext=["Продать 2", "Продать 1", "Ничего", "Купить 1", "Купить 2"],
                title="Действие",
                len=0.8,
                title_font_size=13,
                bgcolor="#1a2236",
            ),
        )

        fig_policy = go.Figure(data=heatmap)
        fig_policy.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=16, r=16, t=30, b=16),
            xaxis=dict(tickmode="linear", dtick=1, title="Час", title_font_size=14),
            yaxis=dict(dtick=1, title="Заряд батареи, кВт·ч", title_font_size=14),
            paper_bgcolor="#1a2236",
            plot_bgcolor="#1a2236",
        )
        st.plotly_chart(fig_policy, use_container_width=True)

        st.markdown(
            '<div class="small-note">🔴 продаём, 🔵 покупаем, серый - сидим ровно.</div>',
            unsafe_allow_html=True,
        )

    st.subheader("📈 Насколько хороша каждая ситуация")
    st.caption(
        "Чем краснее клетка, тем лучше в ней оказаться. Тут учтены не только сегодняшние "
        "деньги, но и все будущие возможности с дисконтом. (т.е. мат ожид по сути)"
    )

    fig_v = px.imshow(
        V.T,
        labels=dict(x="Час", y="Заряд батареи", color="Ценность"),
        x=list(range(24)),
        y=list(range(max_battery + 1)),
        origin="lower",
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    fig_v.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=16, r=16, t=30, b=16),
        xaxis=dict(tickmode="linear", dtick=1, title_font_size=14),
        yaxis=dict(dtick=1, title_font_size=14),
        paper_bgcolor="#1a2236",
        plot_bgcolor="#1a2236",
    )
    st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("---")

    st.subheader("🎲 Что получится за сутки")
    st.caption(
        f"Запускаем стратегию на 24 часа вперёд. С утра в батарее {start_battery} кВт·ч, "
        f"солнце выпадает случайно с шансом {prob_sun:.0%}."
    )

    np.random.seed(42)

    current_b = start_battery
    total_money = 0.0
    history_b, history_a, history_money = [], [], []

    for hour in range(24):
        t = hour % 24
        action = Policy[t, current_b]

        is_day = 8 <= t <= 18
        sun = 2 if (is_day and np.random.rand() < prob_sun) else 0

        total_money -= action * env.prices[t]
        current_b = min(max(current_b + action + sun - 1, 0), max_battery)

        history_b.append(current_b)
        history_a.append(action)
        history_money.append(total_money)

    col_sim_left, col_sim_right = st.columns([1.6, 1])

    with col_sim_left:
        fig_sim = go.Figure()
        fig_sim.add_trace(
            go.Scatter(
                x=np.arange(24),
                y=history_b,
                mode="lines+markers",
                name="Заряд батареи",
                line=dict(width=3, color="#38bdf8"),
                marker=dict(size=6, color="#38bdf8"),
            )
        )
        fig_sim.add_trace(
            go.Bar(
                x=np.arange(24),
                y=history_a,
                name="Действие (покупка/продажа)",
                marker_color="#94a3b8",
                opacity=0.55,
                width=0.8,
            )
        )
        fig_sim.update_layout(
            template="plotly_dark",
            height=520,
            margin=dict(l=16, r=16, t=30, b=16),
            xaxis_title="Час от старта",
            yaxis_title="кВт·ч / действие",
            legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", font_size=13),
            xaxis=dict(title_font_size=14),
            yaxis=dict(title_font_size=14),
            paper_bgcolor="#1a2236",
            plot_bgcolor="#1a2236",
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    with col_sim_right:
        fig_money = go.Figure()
        fig_money.add_trace(
            go.Scatter(
                x=np.arange(24),
                y=history_money,
                mode="lines",
                name="Баланс",
                line=dict(width=3.5, color="#10b981"),
                fill="tozeroy",
                fillcolor="rgba(16,185,129,0.12)",
            )
        )
        fig_money.update_layout(
            template="plotly_dark",
            height=520,
            margin=dict(l=16, r=16, t=30, b=16),
            xaxis_title="Час от старта",
            yaxis_title="Накоплено, у.е.",
            showlegend=False,
            xaxis=dict(title_font_size=14),
            yaxis=dict(title_font_size=14),
            paper_bgcolor="#1a2236",
            plot_bgcolor="#1a2236",
        )
        st.plotly_chart(fig_money, use_container_width=True)

    final_cash = history_money[-1]
    final_battery = history_b[-1]

    m1, m2 = st.columns(2)
    with m1:
        st.metric("💰 Баланс в конце", f"{final_cash:+.1f} у.е.")
    with m2:
        st.metric("🔋 Заряд в конце", f"{final_battery} кВт·ч")


# ================================================================
# Вкладка 2: математика, с нуля
# ================================================================
with tab_math:
    st.title("📖 Как это все работает")
    st.markdown(
        "Тут я разберу немного теорию: что такое состояние, действие, награда,"
        "почему вообще нужна какая-то математика, и как мы находим самую оптимальную стратегию."
    )

    # --- 0. Зачем ---
    st.divider()
    st.header("0. Зачем нужна матеша?")
    st.markdown(
        """
        Представьте, что вы целый день вручную управляете батареей. В 3 ночи решаете
        зарядить, потому что ток дешёвый. В полдень видите солнце и решаете не покупать,
        авось панели сами вытянут. В 18 часов цена скакнула в три раза - продаёте остатки.

        Это работает, пока всё под рукой и вы ничем больше не заняты. Проблема в том, что
        каждое решение влияет на будущее. Если вы потратили заряд утром, вечером продавать
        нечего. Если копили слишком жадно, упёрлись в потолок батареи и солнечная энергия
        пошла впустую. _(ну и представьте если у вас будет куча стохастических параметров, там гроб самому чето делать)_

        Алгоритм должен думать не на один час, а сразу на сутки вперёд, и при этом не
        знать заранее, будет ли в 14:00 солнечно. Ровно для таких задач придумали 
        марковский процесс принятия решений. В чем суть? Мы раскладываем задачу на 4 элемента:
        **состояние**, **действие**, **переход** и **награда**.
        """
    )

    # --- 1. Состояние ---
    st.divider()
    st.header("1. Состояние")
    st.markdown(
        """
        Состояние - это то, где мы находимся. Все, что необходимо для принятия решения.

        У нас в задаче нужно знать всего две вещи: который сейчас час и сколько
        энергии в батарее. И этого достаточно! Цены фиксированы по часам, потребление
        одинаковое. То есть прошлое не играет роли, в этом суть MDP.

        Записывается это так:
        """
    )
    st.latex(
        r"s = (t,\, b), \qquad t \in \{0, 1, \dots, 23\}, \qquad b \in \{0, 1, \dots, B_{\max}\}"
    )
    st.markdown(
        """
        - $t$ - час суток. День зацикливаем.
        - $b$ - сколько кВт·ч сейчас в батарее.
        - $B_{\\max}$ - размер батареи.

        Всего возможных состояний - $24 \\cdot (B_{\\max} + 1)$. При батарее на 10 кВт·ч
        это $24 \\cdot 11 = 264$ состояния. Для каждого нам надо понять, что делать. Дальше
        увидим, как это сделать без прямого перебора.

        И еще раз, процесс называется марковским, так как для принятия решения нам нужно
        только настоящее, но не прошлое. 
        """
    )

    # --- 2. Действия ---
    st.divider()
    st.header("2. Действия - что мы можем сделать")
    st.markdown(
        """
        Каждый час алгоритм выбирает одно из пяти действий:
        """
    )
    st.latex(r"a \in A = \{-2,\ -1,\ 0,\ +1,\ +2\}")
    st.markdown(
        """
        - $-2, -1$ - продаём в сеть, получаем деньги.
        - $0$ - ничего не делаем.
        - $+1, +2$ - покупаем у сети, тратим деньги.

        Не все действия всегда доступны. Если батарея пустая, продавать нечего -
        действие $-2$ невозможно. Если заряд почти на максимуме, покупать $+2$
        некуда. Поэтому в каждом состоянии есть своё подмножество допустимых действий
        $A(s) \\subseteq A$.

        Действий 5, состояний 264. Если бы мы пытались решить перебором, это $5^{264}$
        """
    )

    # --- 3. Переходы ---
    st.divider()
    st.header("3. Что происходит после действия")
    st.markdown(
        """
        После каждого действия время идёт вперёд:
        """
    )
    st.latex(r"t' = (t + 1) \bmod 24")
    st.markdown(
        """
        То есть после 23:00 наступает 0:00 следующего дня. Это детерминированно крч.

        С зарядом батареи интереснее. На него влияют сразу три вещи:

        1. Наше действие $a$. Купили на $+1$ - заряд вырос на 1.
        2. Постоянное потребление дома: 1 кВт каждый час, всегда. Холодильник, роутер,
           свет, всё это тратит ток.
        3. Солнце. Если сейчас день (с 8 до 18) и панелям повезло, они дают $+2$ кВт.
           Если ночь или небо в тучах - ничего.

        Получается такая формула:
        """
    )
    st.latex(r"b' = \max\!\bigl(0,\ \min(B_{\max},\ b + a + \mathrm{sun} - 1)\bigr)")
    st.markdown(
        """
        Солнце - случайная величина:
        """
    )
    st.latex(
        r"""
        \mathrm{sun} =
        \begin{cases}
            2, & \text{с вероятностью } p_{\mathrm{sun}},\ \text{если } 8 \le t \le 18 \\
            0, & \text{в остальных случаях}
        \end{cases}
        """
    )
    st.markdown(
        """
        Ночью солнца нет. Днём есть два
        варианта: солнечно (с шансом $p_{\\mathrm{sun}}$) и нет (с шансом
        $1 - p_{\\mathrm{sun}}$). То есть из одного состояния и действия в течение дня
        мы можем попасть в два разных следующих состояния. Тот самый стохастический элемент,
        из-за которого нужны матожи.

        Формально вероятность перехода обозначают $P(s' \\mid s, a)$ - "шанс попасть
        в состояние $s'$, если из $s$ применить действие $a$".
        """
    )

    # --- 4. Награда ---
    st.divider()
    st.header("4. Награда")
    st.markdown(
        """
        Награда - это деньги, заработанные или потраченные за этот шаг:
        """
    )
    st.latex(r"R(s, a) = -\,a \cdot \mathrm{price}(t)")
    st.markdown(
        """
        Еще я добавил батарею как актив иначе совсем уныло было, поэтому там +2b
        """
    )

    # --- 5. Дисконт ---
    st.divider()
    st.header("5. Дисконтирование")
    st.markdown(
        """
        В общем, нас беспокоит не только мгновенная награда, но а в целом
        весь выигрыш за всю симуляцию. Если симуляция будет идти вечность, то 
        выигрыш будет стремится к бесконечности, не будет что оптимизировать
        Поэтому вводим дисконт
        """
    )
    st.latex(r"G = \mathbb{E}\!\left[\,\sum_{k=0}^{\infty} \gamma^{k}\, r_{k}\,\right]")

    # --- 6. Стратегия ---
    st.divider()
    st.header("6. Стратегия")
    st.markdown(
        """
        Стратегия или же policy $\\pi$ - это правило, которое
        каждому состоянию сопоставляет действие:
        """
    )
    st.latex(r"\pi : S \to A")
    st.markdown(
        """
        То есть для всех 264 состояний у нас прописано, что делать. Если попали в
        $(14, 5)$ - смотрим в таблицу, читаем там, скажем, $-1$, и продаём 1 кВт.

        Лучшая возможная стратегия $\\pi^{*}$ - та, которая даёт максимальный ожидаемый
        дисконтированный доход:
        """
    )
    st.latex(
        r"\pi^{*} = \arg\max_{\pi}\ \mathbb{E}_{\pi}\!\left[\,\sum_{k=0}^{\infty} \gamma^{k}\, r_{k}\,\right]"
    )
    st.markdown(
        """
        Это и есть наша цель. Осталось понять, как её найти, не перебирая
        $5^{264}$ вариантов.
        """
    )

    # --- 7. Ценность ---
    st.divider()
    st.header("7. Ценность состояния")
    st.markdown(
        """
        Вместо того чтобы оценивать стратегии целиком, будем оценивать состояния. 
        Каждому состоянию $s$ припишем число $V^{*}(s)$ - 
        "сколько мы заработаем в среднем, если попадём в $s$ и дальше будем
        играть оптимально (по нашей стратегии)".
        """
    )
    st.latex(
        r"V^{*}(s) = \max_{\pi}\ \mathbb{E}_{\pi}\!\left[\,\sum_{k=0}^{\infty} \gamma^{k}\, r_{k}\,\bigg|\, s_{0} = s\,\right]"
    )

    # --- 8. Беллман ---
    st.divider()
    st.header("8. Уравнение Беллмана")
    st.markdown(
        """
        Ключевое наблюдение. Ценность состояния $s$ - это "сколько заработаем дальше".
        А "дальше" - это один шаг вперёд плюс снова "сколько заработаем дальше" из нового
        состояния. То есть ценность определяется через саму себя.

        Формализуем. Если из $s$ применить действие $a$, мы:

        1. Получим мгновенную награду $R(s, a)$.
        2. С вероятностью $P(s' \\mid s, a)$ окажемся в $s'$, где будущая ценность - $V^{*}(s')$.

        Выбираем лучшую a, а далее усредняем (матож).
        """
    )
    st.latex(
        r"V^{*}(s) \;=\; \max_{a \in A(s)}\ \sum_{s'} P(s' \mid s, a)\,\Bigl[\,R(s, a) + \gamma\, V^{*}(s')\,\Bigr]"
    )
    st.markdown(
        """
        - $\\max_{a}$ - перебор всех допустимых действий в этом состоянии, берём лучшее.
        - $\\sum_{s'} P(s' \\mid s, a)$ - усреднение по всем возможным следующим состояниям
          с их вероятностями.
        - $R(s, a)$ - награда сейчас.
        - $\\gamma V^{*}(s')$ - будущая ценность с дисконтом.

        Это и есть **уравнение Беллмана**. Изначально придумали для управления ракетами ахахах )))

        Хитрость в том, что $V^{*}$ стоит и в левой, и в правой части. Так-то это ваще 
        система уравнений, в нашем случае их 264. Поэтому решение есть.

        Из $V^{*}$ оптимальная стратегия извлекается одним шагом:
        """
    )
    st.latex(
        r"\pi^{*}(s) \;=\; \arg\max_{a \in A(s)}\ \sum_{s'} P(s' \mid s, a)\,\Bigl[\,R(s, a) + \gamma\, V^{*}(s')\,\Bigr]"
    )
    st.markdown(
        """
        Та же формула, только вместо максимума берём действие, которое его даёт.
        """
    )

    # --- 9. Value Iteration ---
    st.divider()
    st.header("9. Value Iteration")
    st.markdown(
        """
        Уравнение Беллмана аналитически особо не решить, тк оно нелинейно. 
        Но есть итеративный алгоритм, который сходится к решению.

        Что делаем: применяем уравнение Беллмана как формулу обновления и
        повторяем, пока значения не перестанут меняться.

        **Шаг 0.** Берём любое начальное приближение. Самое простое - все нули:
        """
    )
    st.latex(r"V_{0}(s) = 0 \qquad \text{для всех } s")
    st.markdown(
        """
        **Шаг $k \\to k+1$.** Для каждого состояния пересчитываем ценность, используя
        текущие значения в правой части:
        """
    )
    st.latex(
        r"V_{k+1}(s) \;=\; \max_{a \in A(s)}\ \sum_{s'} P(s' \mid s, a)\,\Bigl[\,R(s, a) + \gamma\, V_{k}(s')\,\Bigr]"
    )
    st.markdown(
        """
        То есть берём старое $V_k$, подставляем справа, считаем новое $V_{k+1}$.
        Повторяем для всех 264 состояний.

        **Когда останавливаться.** Считаем, насколько сильно изменились значения за
        итерацию:
        """
    )
    st.latex(r"\Delta_{k} \;=\; \max_{s}\, \bigl|\,V_{k+1}(s) - V_{k}(s)\,\bigr|")
    st.markdown(
        """
        Если $\\Delta_k$ меньше некоторого маленького порога $\\theta$ (скажем, $10^{-4}$) -
        останавливаемся. Дальнейшие итерации уже почти ничего не меняют.

        После остановки $V_{k} \\approx V^{*}$, и оптимальная стратегия извлекается через
        $\\arg\\max$.
        """
    )

    # --- 10. Сходимость ---
    st.divider()
    st.header("10. Почему наш алгоритм сходится")
    st.markdown(
        """
        Преобразование, которое делает $V_k$ из $V_{k+1}$ обладает свойством сжатия. 
        Если применить его к двум разным
        функциям ценности, расстояние между ними уменьшится в $\\gamma$ раз:
        """
    )
    st.latex(r"\|\, T V - T U \,\|_{\infty} \;\le\; \gamma\, \|\, V - U \,\|_{\infty}")
    st.markdown(
        """
        По теореме Банаха о неподвижной точке у любого сжимающего оператора
        есть единственная неподвижная точка, и итерации к ней сходятся геометрически
        с тем же коэффициентом $\\gamma$.

        Эта неподвижная точка и есть $V^{*}$. То есть мы гарантированно к ней придём,
        с какого приближения ни начинали бы.
        """
    )

    # --- 11. Связь с интерфейсом ---
    st.divider()
    st.header("11. Немного про графики")
    st.markdown(
        """
        Алгоритм считает $V^{*}$ для всех 264 состояний. Та самая тепловая
        карта **"Насколько хороша каждая ситуация"**. 

        Из $V^{*}$ извлекается $\\pi^{*}$ - тепловая карта **"Что советует делать
        алгоритм"**. Каждая её клетка - готовый совет: "если ты сейчас в этом часе
        с этим зарядом, сделай вот это".
        """
    )
