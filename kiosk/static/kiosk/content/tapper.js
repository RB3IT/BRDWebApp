/**
 * Tapper- A class for generating Short Touch events.
 * 
 * To use Tapper, initialize a new instance with the target canvas to generate events for.
 * 
 * A Tap is defined by a Touch event which ends within a set period of time and is confined
 * within an area of the screen: these are available as the options "delay" and "jitter"
 * respectively.
 * 
 * When a Tap occurs, Tapper will dispatch a new CustomEvent via the canvas:
 * the details property will contain the javascript Touch Event that caused
 * the Tap, and will be updated with "parentX" and "parentY" which gives the
 * Tap coordinates relative to the canvas.
 * 
 * Example Usage:
 * 
 *      var mycanvas = document.getElementById("mycanvas");
 *      var tapper = new Tapper(mycanvas);
 *      mycanvas.addEventListener("tap", console.log);
 * 
 *      // When the screen recieves a Touch that lasts no longer than 500 milliseconds
 *      // and ends no further than 3 pixels from the start point (the defaults for
 *      // delay and jitter), console will log a tap Event, which contains the details
 *      // property previously mentioned.
 * 
 * 
 * */
class Tapper {
    /**
     * Initialize a new Tapper Instance which dispatches Tap Events on a given canvas
     * @param {Element} canvas - An html Canvas Element
     * @param {Object} options - Customization options
     * @param {Number} options.delay - Dispatch Tap if touchend occurs within [delay] milliseconds of touchstart.
     * @param {Number} options.jitter - Dispatch Tap if touchend occurs within [jitter] pixels of touchstart.
     */
    constructor(canvas, options) {
        this.canvas = canvas;
        options = options === undefined ? {} : options;
        this.options = {};
        // Leeway for accidental movement (in pixels) during tap: default 3
        this.options.jitter = options.jitter === undefined ? 3 : parseInt(options.jitter);
        // Length of touch (in milliseconds) that still counts as a tap: default 500
        this.options.delay = options.delay === undefined ? 500 : parseInt(options.delay);
        this.handler = [];
        this.openTouches = null;
        this._newOpenTouches();
        this._registerHandler();
    }

    /**
     * Internal method to generate a new openTouches object. Included as separate
     * function in case openTouches changes type in the future
     * */
    _newOpenTouches() {
        this.openTouches = {};
    }

    /**
     * Registers touch events to this.canvas.addEventListener.
     * If events are already registered for this Tapper instance,
     * those events will be removed.
     * */
    _registerHandler() {
        // This class is only handling touch events for one canvas at a time right now
        if (this.handler.length) this._unregisterHandler();
        let handlers = [
            ["touchstart", this._touchstart.bind(this)],
            ["touchend", this._touchend.bind(this)],
            ["touchcancel", this._touchcancel.bind(this)]
        ];
        for (let [touchtype, callback] of handlers) {
            this.canvas.addEventListener(touchtype, callback);
            this.handler.push([touchtype, callback]);
        }
    }

    /**
     * Remove any eventListeners currently managed by this Tapper instance.
     * */
    _unregisterHandler() {
        for (let [eventtype, handler] of this.handler) {
            this.canvas.removeEventListener(eventtype, handler);
        }
    }

    /**
     * Begin tracking new touches to determine if they qualify as Taps,
     * storing touches in openTouches for future reference.
     * @param {Event} event - touchstart Event
     */
    _touchstart(event) {
        for (let touch of event.changedTouches) {
            touch.timeStamp = event.timeStamp;
            this.openTouches[touch.identifier] = touch;
        }
    }

    /**
     * Compare the touches in the touchend event's changedTouches property
     * to their touchstart event to determine if they qualifies as a Tap.
     * When done, remove each touch from this.openTouches
     * @param {Event} event - touchend Event
     */
    _touchend(event) {
        for (let touch of event.changedTouches) {
            let start = this.openTouches[touch.identifier];
            // Phantom Touch
            if (start === undefined) return;
            // Swipe
            if (Math.abs(touch.screenX - start.screenX) < this.options.jitter || Math.abs(touch.screenY - start.screenY) < this.options.jitter) {
                // Long Press
                if (event.timeStamp - start.timeStamp < this.options.delay) {
                    let bounding = touch.target.getBoundingClientRect();
                    touch.parentX = touch.clientX - bounding.x;
                    touch.parentY = touch.clientY - bounding.y;
                    this._trigger(touch);
                }
            }
            this._removetouch(touch);
        }
        // Flush any Undead Touches if there are no more touches on the screen
        if (!event.touches.length) this._newOpenTouches();
    }

    /**
     * Remove any canceled touches from openTouches.
     * @param {Event} event - touchcancel Event
     */
    _touchcancel(event) {
        this._removetouch(event.changedTouches[0]);
    }

    /**
     * Remove the given touch from openTouches. Kept as a separate function
     * in case openTouches changes in the future.
     * @param {Touch} touch - a Touch object retrieved from a touch event
     */
    _removetouch(touch) {
        delete this.openTouches[touch.identifier];
    }

    /**
     * Dispatch a Tap CustomEvent with the given touchdata via this.canvas
     * @param {Object} touchdata - A modified Touch Object
     */
    _trigger(touchdata) {
        let e = new CustomEvent("tap", { detail: touchdata });
        this.canvas.dispatchEvent(e);
    }
}