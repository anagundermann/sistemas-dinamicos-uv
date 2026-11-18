
/* SISTEMAS DINAMICOS UV - TUTORIAL GUIADO
   Ventana fija, resaltado de varios controles y regreso al inicio.
   Ajuste del paso 3 de Depredador-Presa sin alterar otros laboratorios.
*/
(function () {
    'use strict';

    var escenaActual = null;
    var claveAnterior = '';
    var pendientePosicion = false;
    var guiaEnfocada = false;
    var rellenoOriginal = null;
    var retornoPendiente = false;

    function esPasoModelos() {
        return Boolean(
            escenaActual && escenaActual.abierta &&
            escenaActual.pagina === 'depredador_presa' &&
            escenaActual.objetivo === '.lv-selector-modelo'
        );
    }

    function prepararEspacio() {
        if (!document.body) return;

        if (esPasoModelos()) {
            if (rellenoOriginal === null) {
                rellenoOriginal = document.body.style.paddingBottom;
            }

            // Permite bajar la pagina y subir visualmente el selector.
            document.body.style.paddingBottom = Math.ceil(
                Math.max(650, window.innerHeight * 1.1)
            ) + 'px';
            return;
        }

        // Conservar el espacio hasta terminar el regreso al inicio.
        if (retornoPendiente && rellenoOriginal !== null) return;

        if (rellenoOriginal !== null) {
            document.body.style.paddingBottom = rellenoOriginal;
            rellenoOriginal = null;
        }
    }

    function obtenerObjetivo() {
        if (!escenaActual || !escenaActual.objetivo) return null;

        var elementos;

        try {
            elementos = document.querySelectorAll(escenaActual.objetivo);
        } catch (error) {
            return null;
        }

        var visibles = Array.from(elementos).map(function (elemento) {
            return {
                elemento: elemento,
                rect: elemento.getBoundingClientRect()
            };
        }).filter(function (dato) {
            return dato.rect.width >= 5 && dato.rect.height >= 5;
        });

        if (!visibles.length) return null;

        return {
            elemento: visibles[0].elemento,
            multiple: visibles.length > 1,
            rect: {
                left: Math.min.apply(null, visibles.map(function (e) {
                    return e.rect.left;
                })),
                top: Math.min.apply(null, visibles.map(function (e) {
                    return e.rect.top;
                })),
                right: Math.max.apply(null, visibles.map(function (e) {
                    return e.rect.right;
                })),
                bottom: Math.max.apply(null, visibles.map(function (e) {
                    return e.rect.bottom;
                }))
            }
        };
    }

    function posicionar() {
        pendientePosicion = false;

        var marco = document.getElementById('sd-guia-resalte');
        var tarjeta = document.getElementById('sd-guia-tarjeta');

        if (!marco || !tarjeta) return;

        if (!escenaActual || !escenaActual.abierta) {
            marco.style.display = 'none';
            tarjeta.classList.remove('sd-guia-tarjeta-arriba');
            return;
        }

        tarjeta.classList.add('sd-guia-tarjeta-arriba');

        var objetivo = obtenerObjetivo();

        if (!objetivo) {
            marco.style.display = 'none';
            return;
        }

        var r = objetivo.rect;
        var izq = Math.max(4, r.left - 7);
        var sup = Math.max(4, r.top - 7);
        var der = Math.min(window.innerWidth - 4, r.right + 7);
        var inf = Math.min(window.innerHeight - 4, r.bottom + 7);

        if (der <= izq || inf <= sup) {
            marco.style.display = 'none';
            return;
        }

        marco.style.display = 'block';
        marco.style.left = izq + 'px';
        marco.style.top = sup + 'px';
        marco.style.width = (der - izq) + 'px';
        marco.style.height = (inf - sup) + 'px';
    }

    function solicitarPosicion() {
        if (pendientePosicion) return;

        pendientePosicion = true;
        requestAnimationFrame(posicionar);
    }

    function moverAlObjetivo(clave) {
        if (
            !escenaActual ||
            !escenaActual.abierta ||
            clave !== claveAnterior
        ) return;

        var objetivo = obtenerObjetivo();
        if (!objetivo) return;

        var r = objetivo.rect;
        var tarjeta = document.getElementById('sd-guia-tarjeta');

        if (esPasoModelos()) {
            // Situar el selector debajo de la ventana blanca.
            var finTarjeta = tarjeta
                ? tarjeta.getBoundingClientRect().bottom
                : 0;

            var altoSelector = r.bottom - r.top;

            var superiorDeseado = Math.max(
                finTarjeta + 9,
                (window.innerHeight - altoSelector) / 2 - 45
            );

            // Calcular el desplazamiento usando el documento.
            var scroll = document.scrollingElement ||
                document.documentElement;

            var maximo = Math.max(
                0,
                scroll.scrollHeight - scroll.clientHeight
            );

            var destino = Math.max(0, Math.min(
                maximo,
                scroll.scrollTop + r.top - superiorDeseado
            ));

            window.scrollTo({
                top: destino,
                behavior: 'smooth'
            });

        } else if (
            r.bottom > window.innerHeight - 24 ||
            r.top < 20
        ) {
            if (objetivo.multiple) {
                var altura = r.bottom - r.top;

                var diferencia = altura > window.innerHeight - 48
                    ? r.top - 30
                    : (r.top + r.bottom) / 2 - window.innerHeight / 2;

                window.scrollBy({
                    top: diferencia,
                    behavior: 'smooth'
                });

            } else {
                objetivo.elemento.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'nearest'
                });
            }
        }

        solicitarPosicion();
    }

    function actualizar(escena) {
        escenaActual = escena || null;

        var tarjeta = document.getElementById('sd-guia-tarjeta');
        var overlay = document.getElementById('sd-guia-overlay');

        var pendulo = Boolean(
            escenaActual && escenaActual.abierta &&
            (
                escenaActual.pagina === 'pendulo_simple' ||
                escenaActual.pagina === 'pendulo_doble'
            )
        );

        if (overlay) {
            overlay.classList.toggle('sd-guia-explorable', pendulo);
        }

        if (tarjeta) {
            tarjeta.classList.toggle(
                'sd-guia-tarjeta-extendida',
                pendulo
            );

            tarjeta.setAttribute(
                'aria-modal',
                pendulo ? 'false' : 'true'
            );

            tarjeta.setAttribute(
                'role',
                pendulo ? 'region' : 'dialog'
            );
        }

        prepararEspacio();

        if (!escenaActual || !escenaActual.abierta) {
            claveAnterior = '';
            guiaEnfocada = false;
            solicitarPosicion();
            return;
        }

        if (tarjeta) {
            tarjeta.classList.add('sd-guia-tarjeta-arriba');
        }

        var clave = String(escenaActual.pagina) + ':' +
            String(escenaActual.paso);

        if (clave !== claveAnterior) {
            claveAnterior = clave;

            setTimeout(function () {
                moverAlObjetivo(clave);
            }, 200);
        }

        if (!guiaEnfocada) {
            guiaEnfocada = true;

            setTimeout(function () {
                var panel = document.getElementById(
                    'sd-guia-tarjeta'
                );

                var capa = document.getElementById(
                    'sd-guia-overlay'
                );

                if (
                    panel &&
                    capa &&
                    capa.classList.contains('sd-guia-visible')
                ) {
                    panel.focus({ preventScroll: true });
                }
            }, 180);
        }

        solicitarPosicion();
        setTimeout(solicitarPosicion, 120);
        setTimeout(solicitarPosicion, 350);
        setTimeout(solicitarPosicion, 700);
    }

    // ========================================================
    // REGRESAR AL INICIO ANTES DE RETIRAR EL ESPACIO
    // ========================================================

    function regresarAlInicio() {
        // Dash cierra primero la guia.
        // El espacio temporal permanece mientras la pagina sube.

        setTimeout(function () {
            var inicio = Date.now();

            var scroll = document.scrollingElement ||
                document.documentElement;

            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });

            function revisar() {
                if (
                    scroll.scrollTop <= 3 ||
                    Date.now() - inicio > 1400
                ) {
                    // Seguridad para navegadores con desplazamiento lento.
                    if (scroll.scrollTop > 3) {
                        window.scrollTo(0, 0);
                    }

                    retornoPendiente = false;

                    // Ahora si se retira el espacio temporal.
                    prepararEspacio();
                    solicitarPosicion();
                    return;
                }

                requestAnimationFrame(revisar);
            }

            requestAnimationFrame(revisar);

        }, 200);
    }

    window.addEventListener('resize', function () {
        prepararEspacio();
        solicitarPosicion();
    }, { passive: true });

    window.addEventListener('scroll', solicitarPosicion, {
        passive: true,
        capture: true
    });

    document.addEventListener('keydown', function (evento) {
        if (
            evento.key !== 'Escape' ||
            !escenaActual ||
            !escenaActual.abierta
        ) return;

        var boton = document.getElementById('sd-guia-cerrar');

        if (boton) {
            evento.preventDefault();
            boton.click();
        }
    });

    // ========================================================
    // FINALIZAR GUIA
    // ========================================================

    document.addEventListener('click', function (evento) {
        var origen = evento.target;

        var boton = origen && origen.closest
            ? origen.closest('button')
            : null;

        var tarjeta = document.getElementById(
            'sd-guia-tarjeta'
        );

        if (
            !boton ||
            !tarjeta ||
            !tarjeta.contains(boton)
        ) return;

        var texto = (boton.textContent || '')
            .replace(/\s+/g, ' ')
            .trim();

        if (!/^finalizar\b/i.test(texto)) return;

        retornoPendiente = true;
        regresarAlInicio();

    }, true);

    window.SDTutorial = {
        actualizar: actualizar
    };
})();
