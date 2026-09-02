const productos = [

    {
        nombre: "Accesorios",
        descripcion: "Accesorios para mascotas.",
        precio: 25000,
        imagen: RUTA_PRODUCTOS + "Accesorios.png"
    },

    {
        nombre: "Arena para gatos aroma de fresa",
        descripcion: "Arena sanitaria con aroma de fresa.",
        precio: 18000,
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_aroma_de_fresa.jpg"
    },

    {
        nombre: "Arena para gatos lavanda",
        descripcion: "Arena sanitaria con aroma a lavanda.",
        precio: 18000,
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_lavanda.jpg"
    },

    {
        nombre: "Arena para gatos olor a bosque de pino",
        descripcion: "Arena sanitaria con aroma a bosque de pino.",
        precio: 20000,
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_olor_a_bosque_de_pino.jpg"
    },

    {
        nombre: "Arena para gatos talco para bebé",
        descripcion: "Arena sanitaria con aroma a talco para bebé.",
        precio: 20000,
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_talco_para_bebé.jpg"
    },

    {
        nombre: "Camas para mascotas",
        descripcion: "Camas cómodas para perros y gatos.",
        precio: 65000,
        imagen: RUTA_PRODUCTOS + "Camas_para_mascotas.jpg"
    },

    {
        nombre: "Collares",
        descripcion: "Collares para mascotas.",
        precio: 22000,
        imagen: RUTA_PRODUCTOS + "Collares.jpeg"
    },

    {
        nombre: "Comida de perro premium",
        descripcion: "Alimento premium para perros.",
        precio: 45000,
        imagen: RUTA_PRODUCTOS + "Comida_de_perro_premium.jpeg"
    },

    {
        nombre: "Comida para gatos variedad salmón",
        descripcion: "Alimento para gatos sabor salmón.",
        precio: 42000,
        imagen: RUTA_PRODUCTOS + "Comida_para_gatos_variedad_salmón.jpeg"
    },

    {
        nombre: "Comida para loros variedad exótica",
        descripcion: "Alimento especial para loros.",
        precio: 28000,
        imagen: RUTA_PRODUCTOS + "Comida_para_Loros_variedad_exótica.jpeg"
    },

    {
        nombre: "Comida para perros variedad carne",
        descripcion: "Alimento para perros sabor carne.",
        precio: 40000,
        imagen: RUTA_PRODUCTOS + "Comida_para_perros_variedad_carne.jpeg"
    },

    {
        nombre: "Juguetes",
        descripcion: "Juguetes para mascotas.",
        precio: 15000,
        imagen: RUTA_PRODUCTOS + "juguetes.png"
    },

    {
        nombre: "Kit de aseo profesional",
        descripcion: "Kit completo para el cuidado de tu mascota.",
        precio: 35000,
        imagen: RUTA_PRODUCTOS + "Kit_de_aseo_profesional.jpg"
    },

    {
        nombre: "Shampoo control de olores",
        descripcion: "Shampoo para eliminar malos olores.",
        precio: 18000,
        imagen: RUTA_PRODUCTOS + "Shampoo_control_de_olores.jpg"
    },

    {
        nombre: "Shampoo hidratante",
        descripcion: "Shampoo hidratante para mascotas.",
        precio: 17000,
        imagen: RUTA_PRODUCTOS + "Shampoo_hidratante.jpeg"
    },

    {
        nombre: "Shampoo para cachorros",
        descripcion: "Shampoo especial para cachorros.",
        precio: 16000,
        imagen: RUTA_PRODUCTOS + "Shampoo_para_cachorros.jpg"
    },

    {
        nombre: "Shampoo para pelo blanco",
        descripcion: "Shampoo para mascotas de pelo blanco.",
        precio: 19000,
        imagen: RUTA_PRODUCTOS + "Shampoo_para_pelo_blanco.jpg"
    },

    {
        nombre: "Shampoo repelente de parásitos",
        descripcion: "Protección contra pulgas y garrapatas.",
        precio: 22000,
        imagen: RUTA_PRODUCTOS + "Shampoo_repelente_de_parásitos.jpeg"
    },

    {
        nombre: "Shampoo",
        descripcion: "Shampoo para mascotas.",
        precio: 15000,
        imagen: RUTA_PRODUCTOS + "Shampoo.jpeg"
    }

];



/* ========================================
   ELEMENTOS
======================================== */

const contenedor =
    document.getElementById(
        "contenedor-productos"
    );


const buscador =
    document.getElementById(
        "buscador"
    );



/* ========================================
   MOSTRAR PRODUCTOS
======================================== */

function mostrarProductos(listaProductos) {

    if (!contenedor) {
        return;
    }


    contenedor.innerHTML = "";


    if (listaProductos.length === 0) {

        contenedor.innerHTML = `

            <div class="card">

                <h3>
                    No se encontraron productos
                </h3>

            </div>

        `;

        return;

    }


    listaProductos.forEach(
        producto => {

            const tarjeta =
                document.createElement("div");

            tarjeta.className = "card";


            tarjeta.innerHTML = `

                <div class="imagen-producto">

                    <img
                        src="${producto.imagen}"
                        alt="${producto.nombre}"
                    >

                </div>


                <h3>
                    ${producto.nombre}
                </h3>


                <p class="descripcion-producto">
                    ${producto.descripcion}
                </p>


                <p class="precio-producto">
                    $${producto.precio.toLocaleString("es-CO")}
                </p>


                <button
                    type="button"
                    class="btn-carrito"
                >
                    Agregar al carrito
                </button>

            `;


            const boton =
                tarjeta.querySelector(
                    ".btn-carrito"
                );


            boton.addEventListener(
                "click",
                function() {

                    agregarCarrito(
                        producto.nombre
                    );

                }
            );


            contenedor.appendChild(
                tarjeta
            );

        }
    );

}



/* ========================================
   INICIO
   SOLO 3 PRODUCTOS
======================================== */

mostrarProductos(
    productos.slice(0, 3)
);



/* ========================================
   BUSCADOR
======================================== */

if (buscador) {

    buscador.addEventListener(
        "input",
        function() {


            const texto =
                buscador.value
                .toLowerCase()
                .trim();


            if (texto === "") {

                mostrarProductos(
                    productos.slice(0, 3)
                );

                return;

            }


            const resultado =
                productos.filter(
                    producto => {

                        const nombre =
                            producto.nombre
                            .toLowerCase();


                        const descripcion =
                            producto.descripcion
                            .toLowerCase();


                        return (
                            nombre.includes(texto)
                            ||
                            descripcion.includes(texto)
                        );

                    }
                );


            mostrarProductos(
                resultado
            );

        }
    );


    buscador.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();


                if (
                    contenedor &&
                    buscador.value.trim() !== ""
                ) {

                    contenedor.scrollIntoView({

                        behavior: "smooth",

                        block: "start"

                    });

                }

            }

        }
    );

}



/* ========================================
   OBTENER CARRITO
======================================== */

function obtenerCarrito() {

    const carritoGuardado =
        localStorage.getItem(
            "carrito"
        );


    if (!carritoGuardado) {

        return [];

    }


    try {

        const carrito =
            JSON.parse(
                carritoGuardado
            );


        if (
            Array.isArray(carrito)
        ) {

            return carrito;

        }


    } catch (error) {

        console.error(
            "Error al leer el carrito:",
            error
        );

    }


    return [];

}



/* ========================================
   GUARDAR CARRITO
======================================== */

function guardarCarrito(
    carrito
) {

    localStorage.setItem(

        "carrito",

        JSON.stringify(
            carrito
        )

    );

}



/* ========================================
   AGREGAR AL CARRITO
======================================== */

function agregarCarrito(
    nombreProducto
) {


    const producto =
        productos.find(

            p =>
                p.nombre ===
                nombreProducto

        );


    if (!producto) {

        return;

    }


    let carrito =
        obtenerCarrito();


    const productoExistente =
        carrito.find(

            p =>
                p.nombre ===
                producto.nombre

        );


    if (productoExistente) {

        productoExistente.cantidad =
            (
                productoExistente.cantidad ||
                1
            ) + 1;

    }


    else {

        carrito.push({

            nombre: producto.nombre,

            descripcion:
                producto.descripcion,

            precio: producto.precio,

            imagen: producto.imagen,

            cantidad: 1

        });

    }


    guardarCarrito(
        carrito
    );


    alert(
        producto.nombre +
        " fue agregado al carrito."
    );

}