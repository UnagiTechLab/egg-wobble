#target illustrator
#targetengine "session"

/**
 * EggWobble for Adobe Illustrator (ExtendScript).
 * Same polar formula as Maya egg_wobble.py.
 * Copyright (c) 2026 Unagi Tech Inc.
 * Unagi Tech Inc. v1.2.0 · MIT License (see LICENSE)
 *
 * Modeless palette. Create/Replace run via app.doScript / BridgeTalk
 * with a self-contained host script — palette onClick cannot see
 * app.activeDocument ("there is no document").
 * File: egg_wobble.jsx
 */

(function () {
    if (typeof app === "undefined" || app.name.indexOf("Illustrator") === -1) {
        alert("Adobe Illustrator で実行してください。");
        return;
    }

    var VERSION = "1.2.0";
    var TOOL_NAME = "EggWobble";
    var UI_GLOBAL = "eggWobbleUi";

    var DEFAULTS = {
        seed: 7,
        whiteR: 180,
        wobble: 0.22,
        subdivs: 64,
        yolkR: 70,
        yolkX: -18,
        yolkY: 22,
        stroke: 3
    };

    // Close legacy palette key if present.
    if (typeof $.global.friedEggBlobUi !== "undefined" && $.global.friedEggBlobUi.window) {
        try {
            $.global.friedEggBlobUi.window.close();
        } catch (eLegacy) {}
        $.global.friedEggBlobUi = undefined;
    }

    if (typeof $.global[UI_GLOBAL] !== "undefined" && $.global[UI_GLOBAL].window) {
        if ($.global[UI_GLOBAL].version === VERSION) {
            try {
                $.global[UI_GLOBAL].window.show();
                $.global[UI_GLOBAL].window.active = true;
                return;
            } catch (eReuse) {
                $.global[UI_GLOBAL] = undefined;
            }
        } else {
            try {
                $.global[UI_GLOBAL].window.close();
            } catch (eOld) {}
            $.global[UI_GLOBAL] = undefined;
        }
    }

    /**
     * Host-side create body (string). Runs in Illustrator DOM context.
     * Relies only on cfg / replaceLast literals + $.global.__ewLastName.
     */
    function hostCreateSource(cfg, replaceLast) {
        return (
            "(function(){\n" +
            "var cfg=" +
            uneval(cfg) +
            ";\n" +
            "var replaceLast=" +
            (replaceLast ? "true" : "false") +
            ";\n" +
            "var AMP2=0.35,AMP3=0.55,AMP4=0.25,TENSION=0.25;\n" +
            "function phases(s){return[0.31+s*0.73,1.17+s*1.19,2.04+s*0.47];}\n" +
            "function blobR(th,R,w,seed){var p=phases(seed);var n=AMP2*Math.cos(2*th+p[0])+AMP3*Math.cos(3*th+p[1])+AMP4*Math.cos(4*th+p[2]);return R*(1+w*n);}\n" +
            "function pts(n,R,w,seed,cx,cy){var a=[];for(var i=0;i<n;i++){var th=(2*Math.PI*i)/n;var r=blobR(th,R,w,seed);a.push([cx+r*Math.cos(th),cy+r*Math.sin(th)]);}return a;}\n" +
            "function tans(P){var n=P.length,t=[];for(var i=0;i<n;i++){var a=P[(i-1+n)%n],b=P[(i+1)%n];t.push([(b[0]-a[0])*TENSION,(b[1]-a[1])*TENSION]);}return t;}\n" +
            "function rgb(r,g,b){var c=new RGBColor();c.red=r;c.green=g;c.blue=b;return c;}\n" +
            "function addPath(doc,P,fill,sw){var path=doc.pathItems.add();path.setEntirePath(P);path.closed=true;path.filled=true;path.fillColor=fill;path.stroked=sw>0;if(path.stroked){path.strokeColor=rgb(17,17,17);path.strokeWidth=sw;path.strokeJoin=StrokeJoin.ROUNDENDJOIN;}path.locked=false;var T=tans(P);for(var i=0;i<path.pathPoints.length;i++){var pp=path.pathPoints[i];pp.pointType=PointType.SMOOTH;pp.leftDirection=[P[i][0]-T[i][0],P[i][1]-T[i][1]];pp.rightDirection=[P[i][0]+T[i][0],P[i][1]+T[i][1]];}return path;}\n" +
            "function getDoc(){\n" +
            "  var d=null;\n" +
            "  try{if(app.documents.length>0)d=app.activeDocument;}catch(e){d=null;}\n" +
            "  if(d)return d;\n" +
            "  try{if(app.documents.length>0)d=app.documents[0];}catch(e2){d=null;}\n" +
            "  if(d)return d;\n" +
            "  try{return app.documents.add(DocumentColorSpace.RGB);}catch(e3){}\n" +
            "  try{return app.documents.add();}catch(e4){}\n" +
            "  throw new Error('ドキュメントを開けませんでした。File > New で新規作成してから Create してください。');\n" +
            "}\n" +
            "var doc=getDoc();\n" +
            "if(replaceLast){\n" +
            "  var _ln=(typeof $.global.__ewLastName==='string'&&$.global.__ewLastName)?$.global.__ewLastName:((typeof $.global.__febLastName==='string'&&$.global.__febLastName)?$.global.__febLastName:null);\n" +
            "  if(_ln){try{doc.groupItems.getByName(_ln).remove();}catch(eR){}}\n" +
            "  $.global.__ewLastName=null;$.global.__febLastName=null;\n" +
            "}\n" +
            "var abi=0;try{abi=doc.artboards.getActiveArtboardIndex();}catch(eA){}\n" +
            "var ab=doc.artboards[abi].artboardRect;\n" +
            "var cx=(ab[0]+ab[2])*0.5, cy=(ab[1]+ab[3])*0.5;\n" +
            "var white=addPath(doc,pts(cfg.subdivs,cfg.whiteR,cfg.wobble,cfg.seed,cx,cy),rgb(255,255,255),cfg.stroke);white.name='white';\n" +
            "var yolk=doc.pathItems.ellipse(cy+cfg.yolkY+cfg.yolkR,cx+cfg.yolkX-cfg.yolkR,cfg.yolkR*2,cfg.yolkR*2);\n" +
            "yolk.name='yolk';yolk.filled=true;yolk.fillColor=rgb(255,204,0);yolk.stroked=cfg.stroke>0;\n" +
            "if(yolk.stroked){yolk.strokeColor=rgb(17,17,17);yolk.strokeWidth=cfg.stroke;yolk.strokeJoin=StrokeJoin.ROUNDENDJOIN;}\n" +
            "yolk.locked=false;\n" +
            "var grp=doc.groupItems.add();white.move(grp,ElementPlacement.PLACEATBEGINNING);yolk.move(grp,ElementPlacement.PLACEATBEGINNING);\n" +
            "grp.name='eggWobble_seed'+cfg.seed;grp.locked=false;\n" +
            "$.global.__ewLastName=grp.name;\n" +
            "try{doc.selection=null;grp.selected=true;}catch(eS){}\n" +
            "app.redraw();\n" +
            "})();\n"
        );
    }

    function runHostCreate(cfg, replaceLast) {
        var code = hostCreateSource(cfg, replaceLast);
        // 1) Preferred: doScript in host
        try {
            app.doScript(code, ScriptLanguage.JSX);
            return;
        } catch (eDo) {
            // continue to BridgeTalk
        }
        // 2) BridgeTalk (self-contained — no palette $.global dependency)
        var bt = new BridgeTalk();
        bt.target = "illustrator";
        bt.body = code;
        bt.onError = function (errObj) {
            alert("Create failed:\n" + errObj.body);
        };
        if (!bt.send(2)) {
            // 3) Last resort: direct (may fail on some palette contexts)
            try {
                app.doScript(code, ScriptLanguage.JSX);
            } catch (e2) {
                throw new Error(
                    "ホスト実行に失敗しました。ドキュメントを前面にしてから再試行してください。\n" + e2
                );
            }
        }
    }

    function buildUi() {
        var w = new Window("palette", TOOL_NAME + " v" + VERSION, undefined, {
            resizeable: false,
            closeButton: true
        });
        w.orientation = "column";
        w.alignChildren = ["fill", "top"];
        w.spacing = 6;
        w.margins = 12;

        var liveActive = false;
        var liveBusy = false;
        var lastLiveMs = 0;

        var statusT = w.add(
            "statictext",
            undefined,
            "Create → live sliders → Confirm to lock. Same idea as Maya."
        );
        statusT.alignment = ["fill", "top"];

        function setStatus(msg) {
            statusT.text = msg;
        }

        function readCfg() {
            return {
                seed: Math.round(seedC.get()),
                whiteR: whiteC.get(),
                wobble: wobbleC.get(),
                subdivs: Math.round(subC.get()),
                yolkR: yolkRC.get(),
                yolkX: yolkXC.get(),
                yolkY: yolkYC.get(),
                stroke: strokeC.get()
            };
        }

        function refreshLive(force) {
            if (!liveActive || liveBusy) {
                return;
            }
            var now = new Date().getTime();
            if (!force && now - lastLiveMs < 70) {
                return;
            }
            lastLiveMs = now;
            liveBusy = true;
            try {
                runHostCreate(readCfg(), true);
                setStatus("Live — tweak sliders, then Confirm.");
            } catch (eLive) {
                // Keep UI usable if a mid-drag redraw fails.
            }
            liveBusy = false;
        }

        function startLive() {
            liveActive = true;
            setStatus("Live — tweak sliders, then Confirm.");
        }

        /**
         * Label + slider + edittext. ScriptUI sliders are integer-ish, so
         * `scale` maps UI units → real value (e.g. wobble scale 100 → 0.22).
         */
        function sliderRow(label, def, minV, maxV, scale, decimals) {
            scale = scale || 1;
            decimals = decimals == null ? 0 : decimals;

            function formatVal(v, d) {
                if (d <= 0) {
                    return String(Math.round(v));
                }
                var n = Math.pow(10, d);
                return String(Math.round(v * n) / n);
            }

            var g = w.add("group");
            g.alignment = ["fill", "top"];
            g.add("statictext", undefined, label).preferredSize.width = 118;
            var sMin = Math.round(minV * scale);
            var sMax = Math.round(maxV * scale);
            var sVal = Math.round(def * scale);
            if (sVal < sMin) sVal = sMin;
            if (sVal > sMax) sVal = sMax;
            var s = g.add("slider", undefined, sVal, sMin, sMax);
            s.preferredSize.width = 168;
            var e = g.add("edittext", undefined, formatVal(def, decimals));
            e.preferredSize.width = 54;

            function clampReal(v) {
                if (isNaN(v)) v = def;
                if (v < minV) v = minV;
                if (v > maxV) v = maxV;
                return v;
            }

            var syncing = false;
            s.onChanging = function () {
                if (syncing) return;
                syncing = true;
                e.text = formatVal(s.value / scale, decimals);
                syncing = false;
                refreshLive(false);
            };
            s.onChange = function () {
                if (syncing) return;
                syncing = true;
                e.text = formatVal(s.value / scale, decimals);
                syncing = false;
                refreshLive(true);
            };
            e.onChange = function () {
                if (syncing) return;
                var v = clampReal(parseFloat(e.text, 10));
                syncing = true;
                s.value = Math.round(v * scale);
                e.text = formatVal(v, decimals);
                syncing = false;
                refreshLive(true);
            };

            return {
                get: function () {
                    var v = parseFloat(e.text, 10);
                    if (isNaN(v)) {
                        v = s.value / scale;
                    }
                    return clampReal(v);
                },
                set: function (v, skipLive) {
                    v = clampReal(parseFloat(v, 10));
                    syncing = true;
                    s.value = Math.round(v * scale);
                    e.text = formatVal(v, decimals);
                    syncing = false;
                    if (!skipLive) {
                        refreshLive(true);
                    }
                }
            };
        }

        var seedC = sliderRow("Seed", DEFAULTS.seed, 0, 9999, 1, 0);
        var whiteC = sliderRow("White radius (pt)", DEFAULTS.whiteR, 10, 2000, 1, 0);
        var wobbleC = sliderRow("Wobble", DEFAULTS.wobble, 0, 0.55, 100, 2);
        var subC = sliderRow("Subdivs", DEFAULTS.subdivs, 16, 256, 1, 0);
        var yolkRC = sliderRow("Yolk radius", DEFAULTS.yolkR, 4, 1000, 1, 0);
        var yolkXC = sliderRow("Yolk offset X", DEFAULTS.yolkX, -500, 500, 1, 0);
        var yolkYC = sliderRow("Yolk offset Y", DEFAULTS.yolkY, -500, 500, 1, 0);
        var strokeC = sliderRow("Stroke (pt)", DEFAULTS.stroke, 0.25, 20, 100, 2);

        // Two equal rows (3+3), same button size — easier scan, even width.
        var BTN_W = 96;
        var BTN_H = 28;

        function addBtn(parent, label) {
            var b = parent.add("button", undefined, label);
            b.preferredSize = [BTN_W, BTN_H];
            return b;
        }

        var btns1 = w.add("group");
        btns1.alignment = "center";
        btns1.spacing = 8;
        var createBtn = addBtn(btns1, "Create");
        var replaceBtn = addBtn(btns1, "Replace");
        var confirmBtn = addBtn(btns1, "Confirm");

        var btns2 = w.add("group");
        btns2.alignment = "center";
        btns2.spacing = 8;
        var randomBtn = addBtn(btns2, "Random");
        var resetBtn = addBtn(btns2, "Reset");
        var closeBtn = addBtn(btns2, "Close");

        function applyDefaults() {
            seedC.set(DEFAULTS.seed, true);
            whiteC.set(DEFAULTS.whiteR, true);
            wobbleC.set(DEFAULTS.wobble, true);
            subC.set(DEFAULTS.subdivs, true);
            yolkRC.set(DEFAULTS.yolkR, true);
            yolkXC.set(DEFAULTS.yolkX, true);
            yolkYC.set(DEFAULTS.yolkY, true);
            strokeC.set(DEFAULTS.stroke, true);
            if (liveActive) {
                refreshLive(true);
            } else {
                setStatus("Defaults restored.");
            }
        }

        createBtn.onClick = function () {
            try {
                runHostCreate(readCfg(), false);
                startLive();
            } catch (err) {
                alert("Create failed:\n" + err);
            }
        };

        replaceBtn.onClick = function () {
            try {
                runHostCreate(readCfg(), true);
                startLive();
            } catch (err) {
                alert("Replace failed:\n" + err);
            }
        };

        // Same idea as Maya: new seed, then replace last egg (or create if none).
        randomBtn.onClick = function () {
            seedC.set(Math.floor(Math.random() * 10000), true);
            try {
                runHostCreate(readCfg(), true);
                startLive();
            } catch (err) {
                alert("Random failed:\n" + err);
            }
        };

        resetBtn.onClick = function () {
            applyDefaults();
        };

        confirmBtn.onClick = function () {
            if (!liveActive) {
                setStatus("Nothing to confirm — Create first.");
                return;
            }
            liveActive = false;
            setStatus("Confirmed — egg locked. Create again for a new live session.");
        };

        function teardown() {
            try {
                w.close();
            } catch (eClose) {}
            if ($.global[UI_GLOBAL] && $.global[UI_GLOBAL].window === w) {
                $.global[UI_GLOBAL] = undefined;
            }
        }

        closeBtn.onClick = function () {
            teardown();
        };

        w.onClose = function () {
            if ($.global[UI_GLOBAL] && $.global[UI_GLOBAL].window === w) {
                $.global[UI_GLOBAL] = undefined;
            }
            return true;
        };

        $.global[UI_GLOBAL] = { window: w, version: VERSION };
        w.show();
        return w;
    }

    buildUi();
})();
