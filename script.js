/* TUR-LASER — скрипты. Без зависимостей, работает и на старых телефонах. */
(function () {
    'use strict';

    /* ---------- Аналитика. Имя цели здесь = имя цели в кабинете Метрики, буква в букву ---------- */
    function track(goal) {
        try {
            if (typeof window.ym === 'function' && window.YM_ID) window.ym(window.YM_ID, 'reachGoal', goal);
        } catch (e) { /* счётчик ещё не стоит */ }
    }
    Array.prototype.forEach.call(document.querySelectorAll('[data-goal]'), function (el) {
        el.addEventListener('click', function () { track(el.getAttribute('data-goal')); });
    });

    /* ---------- Год в подвале ---------- */
    var year = document.getElementById('year');
    if (year) year.textContent = String(new Date().getFullYear());

    /* ---------- Интерактив: стираем ржавчину — проявляется VIN ---------- */
    var MONO = '"Montserrat", Arial, sans-serif'; // только для запасной таблички, если фото не загрузились
    var VIN = 'XW8 TURLASER 260001'; // показательный номер, не настоящий

    function initVinLab(root) {
        var canvas = root.querySelector('canvas');
        if (!canvas || !canvas.getContext) return;
        var ctx = canvas.getContext('2d');
        var hint = root.querySelector('.vinlab__hint');
        var meter = root.querySelector('.vinlab__meter b');
        var done = root.querySelector('.vinlab__done');
        var resetBtn = root.querySelector('.vinlab__reset');
        var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var coarse = window.matchMedia('(pointer: coarse)').matches;

        // Полоса, в которой выбит номер: по ней считаем процент очистки
        var BAND = { x0: 0.04, x1: 0.96, y0: 0.36, y1: 0.64 };
        var GX = 40, GY = 8;

        var W = 0, H = 0, dpr = 1, base, rust, rctx, grid, cleaned = 0;
        var finished = false, interacted = false, pointer = null, last = null, sparks = [], raf = 0, fade = 1, autoRaf = 0;
        var photoBase = null, photoRust = null; // фото-слои: табличка и ржавчина (data-base / data-rust у #vinlab)

        // Картинка «по cover»: заполняет w×h целиком, лишнее по краям обрезается
        function cover(g, img, w, h) {
            var s = Math.max(w / img.naturalWidth, h / img.naturalHeight);
            var dw = img.naturalWidth * s, dh = img.naturalHeight * s;
            g.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
        }

        // Грузим оба фото; cb() — когда оба пришли или ушли в ошибку, но не позже чем через 4 с.
        // Не успели к 4 с — рисуем запасную табличку, а пришедшие позже фото подставляем, пока человек не начал тереть.
        function loadPhotos(cb) {
            var list = [['data-base', function (im) { photoBase = im; }], ['data-rust', function (im) { photoRust = im; }]];
            var left = list.length, called = false;
            var timer = setTimeout(go, 4000);
            function go() { if (called) return; called = true; clearTimeout(timer); cb(); }
            function settle() {
                if (--left > 0) return;
                if (!called) go();
                else if (!interacted && !finished && !autoRaf) setup();
            }
            list.forEach(function (it) {
                var src = root.getAttribute(it[0]);
                if (!src) { settle(); return; }
                var im = new Image();
                im.onload = function () { it[1](im); settle(); };
                im.onerror = settle;
                im.src = src;
            });
        }

        function valueNoise(w, h, cells) {
            var gw = cells + 1, gv = new Float32Array(gw * gw), i;
            for (i = 0; i < gv.length; i++) gv[i] = Math.random();
            var out = new Float32Array(w * h);
            for (var y = 0; y < h; y++) {
                var fy = y / h * cells, y0 = Math.floor(fy), ty = fy - y0, y1 = Math.min(y0 + 1, cells);
                ty = ty * ty * (3 - 2 * ty);
                for (var x = 0; x < w; x++) {
                    var fx = x / w * cells, x0 = Math.floor(fx), tx = fx - x0, x1 = Math.min(x0 + 1, cells);
                    tx = tx * tx * (3 - 2 * tx);
                    var a = gv[y0 * gw + x0], b = gv[y0 * gw + x1], c = gv[y1 * gw + x0], d = gv[y1 * gw + x1];
                    out[y * w + x] = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
                }
            }
            return out;
        }

        function drawBase() {
            var c = document.createElement('canvas');
            c.width = W * dpr; c.height = H * dpr;
            var g = c.getContext('2d');
            g.scale(dpr, dpr);
            if (photoBase) { cover(g, photoBase, W, H); return c; }
            var grad = g.createLinearGradient(0, 0, W, H);
            grad.addColorStop(0, '#99A3AE'); grad.addColorStop(0.5, '#C9D0D8'); grad.addColorStop(1, '#8E98A4');
            g.fillStyle = grad; g.fillRect(0, 0, W, H);
            g.globalAlpha = 0.16;
            for (var i = 0; i < H; i += 2) {
                g.fillStyle = (i % 4 === 0) ? '#FFFFFF' : '#5F6975';
                g.fillRect(Math.random() * W * 0.3, i, W * (0.4 + Math.random() * 0.6), 1);
            }
            g.globalAlpha = 1;
            g.strokeStyle = 'rgba(60,70,80,0.55)'; g.lineWidth = 2;
            g.strokeRect(10, 10, W - 20, H - 20);
            g.fillStyle = 'rgba(40,48,58,0.7)';
            g.font = '600 ' + Math.max(10, Math.round(W * 0.024)) + 'px ' + MONO;
            g.fillText('VIN', 22, 34);
            var size = Math.floor(W / 13);
            g.font = '700 ' + size + 'px ' + MONO;
            g.textAlign = 'center'; g.textBaseline = 'middle';
            g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillText(VIN, W / 2 + 2, H / 2 + 2);
            g.fillStyle = '#2A323C'; g.fillText(VIN, W / 2, H / 2);
            return c;
        }

        function drawRust() {
            var c = document.createElement('canvas');
            c.width = W * dpr; c.height = H * dpr;
            var g = c.getContext('2d');
            if (photoRust) {
                cover(g, photoRust, c.width, c.height);          // в пикселях устройства
                g.fillStyle = 'rgba(30,22,16,.25)'; g.fillRect(0, 0, c.width, c.height);
                g.setTransform(dpr, 0, 0, dpr, 0, 0);           // erase() рисует в CSS px
                return c;
            }
            var sw = 72, sh = Math.max(8, Math.round(72 * H / W));
            var small = document.createElement('canvas'); small.width = sw; small.height = sh;
            var sg = small.getContext('2d');
            var img = sg.createImageData(sw, sh), d = img.data;
            var n1 = valueNoise(sw, sh, 5), n2 = valueNoise(sw, sh, 12), n3 = valueNoise(sw, sh, 26);
            for (var i = 0; i < sw * sh; i++) {
                var n = n1[i] * 0.55 + n2[i] * 0.3 + n3[i] * 0.15;
                var t = Math.min(1, Math.max(0, (n - 0.25) / 0.5));
                d[i * 4] = Math.round(66 + 125 * t);
                d[i * 4 + 1] = Math.round(32 + 62 * t);
                d[i * 4 + 2] = Math.round(16 + 22 * t);
                d[i * 4 + 3] = Math.round(218 + 37 * t);
            }
            sg.putImageData(img, 0, 0);
            g.imageSmoothingEnabled = true;
            g.drawImage(small, 0, 0, c.width, c.height);
            var grain = document.createElement('canvas'); grain.width = 128; grain.height = 128;
            var gg = grain.getContext('2d'), gi = gg.createImageData(128, 128), gd = gi.data;
            for (var j = 0; j < 128 * 128; j++) {
                var v = 110 + Math.random() * 140;
                gd[j * 4] = v; gd[j * 4 + 1] = v * 0.55; gd[j * 4 + 2] = v * 0.25; gd[j * 4 + 3] = 64;
            }
            gg.putImageData(gi, 0, 0);
            g.fillStyle = g.createPattern(grain, 'repeat');
            g.fillRect(0, 0, c.width, c.height);
            g.setTransform(dpr, 0, 0, dpr, 0, 0);
            return c;
        }

        function erase(x, y) {
            var r = Math.max(16, W * 0.055);
            var gr = rctx.createRadialGradient(x, y, 0, x, y, r);
            gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(0.55, 'rgba(0,0,0,0.85)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
            rctx.globalCompositeOperation = 'destination-out';
            rctx.fillStyle = gr;
            rctx.beginPath(); rctx.arc(x, y, r, 0, Math.PI * 2); rctx.fill();
            var cr = r * 0.65, bw = (BAND.x1 - BAND.x0) * W, bh = (BAND.y1 - BAND.y0) * H;
            for (var gy = 0; gy < GY; gy++) {
                var cy = BAND.y0 * H + (gy + 0.5) / GY * bh;
                if (Math.abs(cy - y) > cr) continue;
                for (var gx = 0; gx < GX; gx++) {
                    var idx = gy * GX + gx;
                    if (grid[idx]) continue;
                    var cx = BAND.x0 * W + (gx + 0.5) / GX * bw;
                    if ((cx - x) * (cx - x) + (cy - y) * (cy - y) <= cr * cr) { grid[idx] = 1; cleaned++; }
                }
            }
        }

        function spawnSparks(x, y) {
            if (reduced) return;
            for (var i = 0; i < 3; i++) {
                sparks.push({ x: x, y: y, vx: (Math.random() - 0.5) * 4, vy: -Math.random() * 3 - 0.5, life: 0.7 + Math.random() * 0.3 });
            }
            if (sparks.length > 80) sparks.splice(0, sparks.length - 80);
        }

        function strokeTo(x, y) {
            if (last) {
                var dx = x - last.x, dy = y - last.y, dist = Math.sqrt(dx * dx + dy * dy), step = Math.max(4, W * 0.015);
                for (var s = step; s < dist; s += step) erase(last.x + dx * s / dist, last.y + dy * s / dist);
            }
            erase(x, y);
            last = { x: x, y: y };
            spawnSparks(x, y);
            updateMeter();
        }

        function updateMeter() {
            var pct = Math.round(cleaned / (GX * GY) * 100);
            if (meter) meter.textContent = pct + '%';
            if (pct >= 85 && !finished) finish();
        }

        function finish() {
            finished = true;
            pointer = null; last = null;
            if (hint) hint.classList.add('vinlab__hint--hidden');
            if (done) done.classList.add('vinlab__done--show');
            if (resetBtn && !coarse) { resetBtn.hidden = false; resetBtn.classList.add('vinlab__reset--show'); }
            if (meter) meter.textContent = '100%';
            track('vin_cleaned');
            var t0 = performance.now();
            (function fadeOut(now) {
                fade = reduced ? 0 : Math.max(0, 1 - (now - t0) / 700);
                render();
                if (fade > 0) requestAnimationFrame(fadeOut);
            })(t0);
        }

        function render() {
            ctx.clearRect(0, 0, W, H);
            ctx.drawImage(base, 0, 0, W, H);
            if (fade > 0) { ctx.globalAlpha = fade; ctx.drawImage(rust, 0, 0, W, H); ctx.globalAlpha = 1; }
            for (var i = sparks.length - 1; i >= 0; i--) {
                var p = sparks[i];
                p.x += p.vx; p.y += p.vy; p.vy += 0.15; p.life -= 0.04;
                if (p.life <= 0) { sparks.splice(i, 1); continue; }
                ctx.globalAlpha = p.life; ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x - p.vx * 2, p.y - p.vy * 2); ctx.stroke();
            }
            ctx.globalAlpha = 1;
            if (pointer && !finished) {
                var g = ctx.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, 44);
                g.addColorStop(0, 'rgba(119,207,248,0.6)'); g.addColorStop(0.4, 'rgba(119,207,248,0.18)'); g.addColorStop(1, 'rgba(119,207,248,0)');
                ctx.fillStyle = g; ctx.beginPath(); ctx.arc(pointer.x, pointer.y, 44, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = 'rgba(119,207,248,0.35)'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(W * 0.92, -10); ctx.lineTo(pointer.x, pointer.y); ctx.stroke();
                ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.arc(pointer.x, pointer.y, 3, 0, Math.PI * 2); ctx.fill();
            }
            if (sparks.length && !raf) raf = requestAnimationFrame(function () { raf = 0; render(); });
        }

        function setup() {
            var rect = root.getBoundingClientRect();
            W = Math.max(1, Math.round(rect.width)); H = Math.max(1, Math.round(rect.height));
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            canvas.width = W * dpr; canvas.height = H * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            base = drawBase();
            rust = drawRust();
            rctx = rust.getContext('2d');
            grid = new Uint8Array(GX * GY); cleaned = 0;
            finished = false; fade = 1; last = null; pointer = null; sparks = [];
            if (done) done.classList.remove('vinlab__done--show');
            if (resetBtn) { resetBtn.classList.remove('vinlab__reset--show'); resetBtn.hidden = true; }
            if (hint) hint.classList.remove('vinlab__hint--hidden');
            if (meter) meter.textContent = '0%';
            render();
        }

        function pos(e) {
            var r = canvas.getBoundingClientRect();
            return { x: e.clientX - r.left, y: e.clientY - r.top };
        }
        function userStart() {
            if (interacted) return;
            interacted = true;
            if (hint) hint.classList.add('vinlab__hint--hidden');
            if (autoRaf) { cancelAnimationFrame(autoRaf); autoRaf = 0; }
        }

        canvas.addEventListener('pointerdown', function (e) {
            if (finished || coarse) return;
            userStart();
            pointer = pos(e); last = null; strokeTo(pointer.x, pointer.y); render();
        });
        canvas.addEventListener('pointermove', function (e) {
            if (finished || coarse) return;
            if (e.pointerType !== 'mouse' && !e.buttons) return; // палец: только при касании
            userStart();
            pointer = pos(e); strokeTo(pointer.x, pointer.y); render();
        });
        canvas.addEventListener('pointerup', function () { last = null; });
        canvas.addEventListener('pointerleave', function () { pointer = null; last = null; render(); });
        canvas.addEventListener('pointercancel', function () { pointer = null; last = null; render(); });

        if (resetBtn) resetBtn.addEventListener('click', function () { interacted = false; setup(); track('vin_reset'); });

        // На телефоне интерактива нет: луч сам проходит змейкой по полосе номера и дочищает до конца
        function autoDemo() {
            if (finished || autoRaf) return;
            if (reduced) { finish(); return; }
            var t0 = performance.now(), dur = 6500, rows = 3, bandH = (BAND.y1 - BAND.y0) * H;
            (function frame(now) {
                if (finished) { autoRaf = 0; return; }
                var t = Math.min(1, (now - t0) / dur);
                var p = t * rows, row = Math.min(rows - 1, Math.floor(p)), f = p - row;
                var along = row % 2 ? 1 - f : f; // туда — обратно — туда
                var x = W * (0.04 + 0.92 * along);
                var y = BAND.y0 * H + bandH * (row + 0.5) / rows + Math.sin(t * Math.PI * 11) * bandH * 0.12;
                pointer = { x: x, y: y }; strokeTo(x, y); render();
                if (t < 1) { autoRaf = requestAnimationFrame(frame); return; }
                autoRaf = 0; pointer = null;
                if (!finished) finish(); else render();
            })(t0);
        }

        loadPhotos(function () {
            setup();
            root.classList.add('vinlab--ready');
            if (coarse && 'IntersectionObserver' in window) {
                var seen = false;
                new IntersectionObserver(function (entries) {
                    if (entries[0].isIntersecting && !seen) { seen = true; setTimeout(autoDemo, 900); }
                }, { threshold: 0.6 }).observe(root);
            }
        });
        var resizeTimer = 0;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                if (Math.round(root.getBoundingClientRect().width) !== W) { interacted = false; setup(); if (coarse) setTimeout(autoDemo, 400); }
            }, 200);
        });
    }
    var lab = document.getElementById('vinlab');
    if (lab) initVinLab(lab);

    /* ---------- Видео: играет только на экране, без звука ---------- */
    var vid = document.querySelector('.showreel__video');
    if (vid && 'IntersectionObserver' in window) {
        // Автозапуск запрещён (энергосбережение на iPhone, экономия трафика на Android) — показываем кнопки плеера,
        // иначе ролик навсегда остаётся картинкой. AbortError — это pause() во время запуска, не запрет.
        var manualPlay = function () {
            vid.controls = true;
            if (vid.parentNode && vid.parentNode.classList) vid.parentNode.classList.add('proc__video--manual');
        };
        new IntersectionObserver(function (entries) {
            if (entries[0].isIntersecting) {
                var p = vid.play();
                if (p && p.catch) p.catch(function (err) { if (!err || err.name !== 'AbortError') manualPlay(); });
            }
            else vid.pause();
        }, { threshold: 0.2 }).observe(vid);
    }

    /* ---------- Нижняя панель прячется, когда видны контакты ---------- */
    var mbar = document.getElementById('mbar'), zay = document.getElementById('kontakty');
    if (mbar && zay && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            mbar.classList.toggle('mbar--hidden', entries[0].isIntersecting);
        }, { threshold: 0.2 }).observe(zay);
    }

    /* ---------- Нижняя панель не появляется, пока кнопки первого экрана видны или ещё ниже края экрана ---------- */
    // На низких экранах (iPhone SE в Safari) кнопки стоят ниже края — панель закрыла бы заголовок.
    // Нижняя граница «экрана» продлена: кнопки ниже края считаются видимыми, и прыжок по якорю это не ломает.
    var heroCta = document.querySelector('#hero .cta');
    if (mbar && heroCta) {
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (entries) {
                var e = entries[0];
                mbar.classList.toggle('mbar--early', e.isIntersecting || e.boundingClientRect.top > 0);
            }, { rootMargin: '0px 0px 10000px 0px' }).observe(heroCta);
        } else mbar.classList.remove('mbar--early');
    }

    /* ---------- Нижняя панель уходит, только пока подписи или точки ленты «до / после» в нижних 90px экрана ---------- */
    // Панель занимает 68px снизу: фото ленты она перекрывает, как любую картинку, а подписи и точки не прячет.
    // Корень наблюдателя — полоса 90px у нижнего края; высота окна меняется (строка адреса в Safari) — полоса пересчитывается.
    var baUnder = document.querySelectorAll('.ba figcaption, .ba .dots');
    if (mbar && baUnder.length && 'IntersectionObserver' in window) {
        var underIO = null, underOn = [], underTimer = 0;
        var watchUnder = function () {
            if (underIO) underIO.disconnect();
            underOn = []; // первый вызов нового наблюдателя приходит по всем целям сразу
            underIO = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    var k = underOn.indexOf(e.target);
                    if (e.isIntersecting && k < 0) underOn.push(e.target);
                    else if (!e.isIntersecting && k >= 0) underOn.splice(k, 1);
                });
                mbar.classList.toggle('mbar--lane', underOn.length > 0);
            }, { rootMargin: -Math.max(0, window.innerHeight - 90) + 'px 0px 0px 0px' });
            Array.prototype.forEach.call(baUnder, function (el) { underIO.observe(el); });
        };
        watchUnder();
        window.addEventListener('resize', function () {
            clearTimeout(underTimer);
            underTimer = setTimeout(watchUnder, 200);
        });
    }

    /* ---------- Лента «до / после»: счётчик, точки, стрелки ---------- */
    var lane = document.querySelector('.ba .track');
    if (lane) {
        var slides = lane.querySelectorAll('.pair');
        var count = document.querySelector('.ba__count b');
        var dots = document.querySelectorAll('.ba .dots i');
        var prev = document.querySelector('.ba__nav [data-dir="-1"]'), next = document.querySelector('.ba__nav [data-dir="1"]');
        var laneBehavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        var nearest = function () {
            var x = lane.scrollLeft, best = 0;
            for (var i = 1; i < slides.length; i++) {
                if (Math.abs(slides[i].offsetLeft - x) < Math.abs(slides[best].offsetLeft - x)) best = i;
            }
            return best;
        };
        var paint = function () {
            var end = lane.scrollLeft + lane.clientWidth >= lane.scrollWidth - 4;
            var i = end ? slides.length - 1 : nearest();
            if (count) count.textContent = (i < 9 ? '0' : '') + (i + 1);
            Array.prototype.forEach.call(dots, function (d, k) { d.classList.toggle('on', k === i); });
            if (prev) prev.disabled = lane.scrollLeft < 4;
            if (next) next.disabled = end;
        };
        var go = function (d) {
            var i = Math.max(0, Math.min(slides.length - 1, nearest() + d));
            lane.scrollTo({ left: slides[i].offsetLeft, behavior: laneBehavior });
        };
        if (prev) prev.addEventListener('click', function () { go(-1); });
        if (next) next.addEventListener('click', function () { go(1); });
        var laneRaf = 0;
        lane.addEventListener('scroll', function () {
            cancelAnimationFrame(laneRaf); laneRaf = requestAnimationFrame(paint);
        }, { passive: true });
        paint();
    }

    /* ---------- Появление при прокрутке: только H2, видео и лента ---------- */
    var rv = document.querySelectorAll('.rv');
    if (rv.length && 'IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.classList.add('js-rv');
        var rvIo = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { e.target.classList.add('rv--in'); rvIo.unobserve(e.target); }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
        Array.prototype.forEach.call(rv, function (el) { rvIo.observe(el); });
    }
})();
