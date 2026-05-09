from dataclasses import dataclass

import streamlit as st


@dataclass
class SidebarConfig:
    max_battery: int
    prob_sun: float
    start_battery: int
    night_price: int
    day_price: int
    peak_price: int


def render_sidebar() -> SidebarConfig:
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
            value=min(2, max_battery),
            step=1,
            help="С чего стартуем при моделировании суток.",
        )

        st.markdown("---")
        st.markdown("### 💸 Тарифы, у.е./кВт·ч")
        st.markdown(
            '<p class="small-note">Поиграйтесь с ценами '
            "и посмотрите, как сдвигается стратегия.</p>",
            unsafe_allow_html=True,
        )

        night_price = st.slider(
            "🌙 Ночь (0-6 и 21-23)",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
            help="Самый дешёвый тариф, обычно ночью.",
        )
        day_price = st.slider(
            "☀️ День (7-16)",
            min_value=1,
            max_value=100,
            value=15,
            step=1,
            help="Базовый дневной тариф.",
        )
        peak_price = st.slider(
            "🔥 Пик (17-20)",
            min_value=1,
            max_value=200,
            value=50,
            step=1,
            help="Часы пиковой нагрузки, дороже всего.",
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

    return SidebarConfig(
        max_battery=max_battery,
        prob_sun=prob_sun,
        start_battery=start_battery,
        night_price=night_price,
        day_price=day_price,
        peak_price=peak_price,
    )
