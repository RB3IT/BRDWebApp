function showBubble(target, message) {
    /* Shows an error bubble near the given target */

    let bubble = $(`<div class="errorbubble-container">
    <div class="errorbubble">
      <span>${message}</span>
    </div>
  </div>`);
    let offset = target.offset();
    let [x, y] = [offset.left, offset.top];
    let h = target.height();
    let top = y + h + 15;
    let left = x + 5;
    $("body").append(bubble);
    bubble.css({ top: `${top}px`, left: `${left}px` });
    bubble.ele = target;
    return bubble;
};

function blurBubble(ele, message) {
    /* Shows the message until the target element is blurred */
    let bubble = showBubble(ele, message);
    f = function () {
        bubble.remove();
        bubble.ele.off("blur.bubble");
        bubble.off("click.bubble","*")
    };
    bubble.ele.on('blur.bubble', f);
    bubble.on("click.bubble","*",f)
}