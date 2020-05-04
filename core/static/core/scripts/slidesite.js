/* Slide Site
 * 
 * Navigates between anchors on a page, hiding all other anchors.
 * On navigation, new "page" will slide in while current "page" will slide out.
 * 
 */

var SlideSite = function (frame,firstpage) {
    let self = this;
    if (typeof frame === "undefined") frame = document.body;
    self.frame = $(frame);
    self.current = undefined;

    self.setupLinks = function (content) {
        /* Change functionality of links in the given elements to use NavTo instead of normal link functionality */
        if (content === undefined) content = frame;
        $(content).find(".nav").click(function () { self.navTo(this.getAttribute("href")); return false; });
    };

    self.navTo = function (ele) {
        /* Navigates to the given ele, hiding the current */
        ele = $(ele);
        console.log('>',ele)
        if (ele === undefined) throw new Error("Invalid ele");
        if (typeof ele === "String") ele = self.frame.find(ele);
        console.log('>>', ele)
        console.log("<<", self.current);
        if (ele[0] === self.current[0]) return;
        self.hide(self.current);
        self.current = ele;
        self.show(ele);
    };

    self.show = function (ele) {
    /* Slides the given page in */
        console.log("!!", ele);
        $(ele).css({"left": "-100%" }).removeClass("hidden").animate({ "left": "0" }, { always: function (ele) { console.log("&&", $(ele));  } });
        //$(ele).animate({ "left": "0" }, { always: ele => $(ele).removeClass("hidden") });
    };

    self.hide = function (ele) {
    /* Slides the given page out */
        console.log("??", ele);
        $(ele).animate({ "left": "100%" }, { always: function () { console.log("$$", this, $(this)); $(this).addClass("hidden"); console.log($(this).attr("class")); }});
        //$(ele).animate({ "right": "-100%" }, { always: ele => $(ele).addClass("hidden") });
    };

    (function (){
    /* Setup */
        console.log("0)", firstpage, typeof firstpage, typeof firstpage === "undefined", self.frame, self.frame.children(".page"), self.frame.children(".page").first())
        firstpage = typeof firstpage === "undefined" ? self.frame.children(".page").first() : $(firstpage);

        console.log("1)", firstpage);
        self.frame.children(".page").each((ind, ele) => $(ele).addClass("hidden"));
        self.show(firstpage);
        self.current = firstpage;
        console.log("2)", self.current);
    })();

    return self;

};