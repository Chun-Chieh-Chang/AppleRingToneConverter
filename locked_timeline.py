import streamlit as st


_timeline = st.components.v2.component(
    "locked_timeline",
    html="""
    <div class="label">拖動整段 30 秒區間</div>
    <div class="track">
        <div class="selection" role="slider" tabindex="0" aria-label="移動 30 秒選取區間"></div>
    </div>
    <div class="times">
        <span>起點 <strong class="start"></strong></span>
        <span>終點 <strong class="end"></strong></span>
        <span>總長度 <strong>30 秒</strong></span>
    </div>
    """,
    css="""
    .label, .times { color: var(--st-text-color); font-size: 0.875rem; }
    .track {
        position: relative;
        height: 44px;
        cursor: pointer;
        touch-action: pan-y;
        user-select: none;
    }
    .track::before {
        content: "";
        position: absolute;
        inset: 17px 0;
        border-radius: 5px;
        background: var(--st-border-color);
    }
    .selection {
        position: absolute;
        top: 7px;
        height: 30px;
        border-radius: 6px;
        background: var(--st-primary-color);
        cursor: grab;
    }
    .selection::before { content: ""; position: absolute; inset: -7px 0; }
    .selection:active { cursor: grabbing; }
    .selection:focus-visible { outline: 2px solid var(--st-text-color); outline-offset: 2px; }
    .times { display: flex; flex-wrap: wrap; gap: 4px 20px; }
    .times strong { font-variant-numeric: tabular-nums; }
    """,
    js="""
    export default function ({ data, parentElement, setStateValue }) {
        const track = parentElement.querySelector(".track");
        const selection = parentElement.querySelector(".selection");
        const startLabel = parentElement.querySelector(".start");
        const endLabel = parentElement.querySelector(".end");
        const { duration, length } = data;
        const max = duration - length;
        let start = data.start;
        let drag;

        function time(ticks) {
            const seconds = Math.floor(ticks / 100);
            const clock = [Math.floor(seconds / 3600), Math.floor(seconds / 60) % 60, seconds % 60]
                .map(part => String(part).padStart(2, "0")).join(":");
            return ticks % 100 ? clock + "." + String(ticks % 100).padStart(2, "0") : clock;
        }

        function show(value) {
            start = Math.max(0, Math.min(max, Math.round(value)));
            selection.style.left = (100 * start / duration) + "%";
            selection.setAttribute("aria-valuenow", start / 100);
            selection.setAttribute("aria-valuetext", time(start) + " 至 " + time(start + length));
            startLabel.textContent = time(start);
            endLabel.textContent = time(start + length);
        }

        function pointerTime(event) {
            const rect = track.getBoundingClientRect();
            return duration * (event.clientX - rect.left) / rect.width;
        }

        selection.style.width = (100 * length / duration) + "%";
        selection.setAttribute("aria-valuemin", 0);
        selection.setAttribute("aria-valuemax", max / 100);
        show(start);

        track.onpointerdown = event => {
            if (drag || !event.isPrimary || event.button !== 0) return;
            const position = pointerTime(event);
            const offset = selection.contains(event.target) ? position - start : length / 2;
            drag = { id: event.pointerId, offset, original: start };
            selection.focus({ preventScroll: true });
            track.setPointerCapture(event.pointerId);
            show(position - offset);
        };
        track.onpointermove = event => {
            if (drag?.id === event.pointerId) show(pointerTime(event) - drag.offset);
        };
        track.onpointerup = event => {
            if (drag?.id !== event.pointerId) return;
            show(pointerTime(event) - drag.offset);
            const { original } = drag;
            drag = undefined;
            if (original !== start) setStateValue("start", start);
        };
        track.onlostpointercapture = event => {
            if (drag?.id !== event.pointerId) return;
            show(drag.original);
            drag = undefined;
        };
        selection.onkeydown = event => {
            const targets = {
                ArrowLeft: start - 100, ArrowDown: start - 100,
                ArrowRight: start + 100, ArrowUp: start + 100,
                Home: 0, End: max,
            };
            if (!Object.hasOwn(targets, event.key)) return;
            event.preventDefault();
            const previous = start;
            show(targets[event.key]);
            if (previous !== start) setStateValue("start", start);
        };
    }
    """,
)


def select_locked_start(*, duration, length, start, key):
    """Place the fixed-length window using hundredths of a second."""
    max_start = duration - length
    initial = min(max(start, 0), max_start)
    stored_start = st.session_state.get(key, {}).get("start")
    current = min(max(stored_start, 0), max_start) if isinstance(stored_start, int) else initial
    result = _timeline(
        data={"duration": duration, "length": length, "start": current},
        key=key,
        default={"start": initial},
        on_start_change=lambda: None,
    )
    return min(max(result.start, 0), max_start) if isinstance(result.start, int) else current
