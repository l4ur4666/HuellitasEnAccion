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


const contenedor = document.getElementById("contenedor-productos");
const buscador = document.getElementById("buscador");


// ========================================
// MOSTRAR PRODUCTOS
// ========================================

function mostrarProductos(listaProductos) {

    contenedor.innerHTML = "";

    if (listaProductos.length === 0) {

        contenedor.innerHTML = `
            <div class="card">
                <h3>No se encontraron productos.</h3>
            </div>
        `;

        return;
    }

    listaProductos.forEach(producto => {

        contenedor.innerHTML += `

            <div class="card">

                <img
                    src="${producto.imagen}"
                    alt="${producto.nombre}"
                >

                <h3>${producto.nombre}</h3>

                <p>${producto.descripcion}</p>

                <p>
                    <strong>
                        💰 $${producto.precio.toLocaleString("es-CO")}
                    </strong>
                </p>

                <button
                    class="btn-carrito"
                    onclick="agregarCarrito('${producto.nombre}')"
                >
                    🛒 Agregar al carrito
                </button>

            </div>

        `;

    });

}


// ========================================
// MOSTRAR SOLO 3 PRODUCTOS AL INICIAR
// ========================================

mostrarProductos(productos.slice(0, 3));


// ========================================
// BUSCADOR
// ========================================

buscador.addEventListener("keyup", function(e) {

    const texto = buscador.value.toLowerCase();

    const resultado = productos.filter(producto =>

        producto.nombre.toLowerCase().includes(texto) ||

        producto.descripcion.toLowerCase().includes(texto)

    );

    mostrarProductos(resultado);


    if (e.key === "Enter") {

        document.getElementById("contenedor-productos").scrollIntoView({
            behavior: "smooth"
        });

    }

});


// ========================================
// MOSTRAR / OCULTAR BUSCADOR
// ========================================

function mostrarBuscador() {

    if (
        buscador.style.display === "none" ||
        buscador.style.display === ""
    ) {

        buscador.style.display = "block";

        buscador.focus();

    } else {

        buscador.style.display = "none";

    }

}


// ========================================
// CARRITO
// ========================================

let productoSeleccionado = "";


// Obtener carrito guardado
function obtenerCarrito() {

    const carritoGuardado = localStorage.getItem("carrito");

    if (carritoGuardado) {

        return JSON.parse(carritoGuardado);

    }

    return [];

}


// Guardar carrito
function guardarCarrito(carrito) {

    localStorage.setItem("carrito", JSON.stringify(carrito));

}


// ========================================
// AGREGAR PRODUCTO AL CARRITO
// ========================================

function agregarCarrito(nombreProducto) {

    productoSeleccionado = nombreProducto;

    document.getElementById("mensaje-modal").innerHTML =

        "💖 ¿Deseas agregar <b>" +
        nombreProducto +
        "</b> al carrito?";


    document.getElementById("modal-carrito").style.display = "flex";

}


// ========================================
// CANCELAR CARRITO
// ========================================

document.getElementById("cancelar").onclick = function() {

    document.getElementById("modal-carrito").style.display = "none";

};


// ========================================
// ACEPTAR CARRITO
// ========================================

document.getElementById("aceptar").onclick = function() {

    document.getElementById("modal-carrito").style.display = "none";


    // Buscar el producto completo
    const producto = productos.find(
        p => p.nombre === productoSeleccionado
    );


    if (producto) {

        let carrito = obtenerCarrito();


        // Comprobar si ya está en el carrito
        const yaExiste = carrito.some(
            p => p.nombre === producto.nombre
        );


        // Si no está, guardarlo
        if (!yaExiste) {

            carrito.push(producto);

            guardarCarrito(carrito);

        }

    }


    document.getElementById("mensaje-exito").innerHTML =

        "🛒✨ <b>" +
        productoSeleccionado +
        "</b> fue agregado al carrito.<br><br>" +

        "Gracias por comprar en <b>Huellitas En Acción</b> 💖";


    document.getElementById("modal-exito").style.display = "flex";

};


// ========================================
// CERRAR MENSAJE DE ÉXITO
// ========================================

document.getElementById("cerrar-exito").onclick = function() {

    document.getElementById("modal-exito").style.display = "none";

};


// ========================================
// CARRITO FLOTANTE DE LA ESQUINA
// ========================================

const carritoFlotante = document.querySelector(".carrito");


if (carritoFlotante) {

    carritoFlotante.style.cursor = "pointer";


    carritoFlotante.addEventListener("click", function() {

        window.location.href = "/carrito";

    });

}