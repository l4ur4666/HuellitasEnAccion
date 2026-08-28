const productos = [

    {
        nombre: "Accesorios",
        descripcion: "Accesorios para mascotas.",
        imagen: RUTA_PRODUCTOS + "Accesorios.png"
    },

    {
        nombre: "Arena para gatos aroma de fresa",
        descripcion: "Arena sanitaria con aroma de fresa.",
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_aroma_de_fresa.jpg"
    },

    {
        nombre: "Arena para gatos lavanda",
        descripcion: "Arena sanitaria con aroma a lavanda.",
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_lavanda.jpg"
    },

    {
        nombre: "Arena para gatos olor a bosque de pino",
        descripcion: "Arena sanitaria con aroma a bosque de pino.",
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_olor_a_bosque_de_pino.jpg"
    },

    {
        nombre: "Arena para gatos talco para bebé",
        descripcion: "Arena sanitaria con aroma a talco para bebé.",
        imagen: RUTA_PRODUCTOS + "Arena_para_gatos_talco_para_bebé.jpg"
    },

    {
        nombre: "Camas para mascotas",
        descripcion: "Camas cómodas para perros y gatos.",
        imagen: RUTA_PRODUCTOS + "Camas_para_mascotas.jpg"
    },

    {
        nombre: "Collares",
        descripcion: "Collares para mascotas.",
        imagen: RUTA_PRODUCTOS + "Collares.jpeg"
    },

    {
        nombre: "Comida de perro premium",
        descripcion: "Alimento premium para perros.",
        imagen: RUTA_PRODUCTOS + "Comida_de_perro_premium.jpeg"
    },

    {
        nombre: "Comida para gatos variedad salmón",
        descripcion: "Alimento para gatos sabor salmón.",
        imagen: RUTA_PRODUCTOS + "Comida_para_gatos_variedad_salmón.jpeg"
    },

    {
        nombre: "Comida para loros variedad exótica",
        descripcion: "Alimento especial para loros.",
        imagen: RUTA_PRODUCTOS + "Comida_para_Loros_variedad_exótica.jpeg"
    },

    {
        nombre: "Comida para perros variedad carne",
        descripcion: "Alimento para perros sabor carne.",
        imagen: RUTA_PRODUCTOS + "Comida_para_perros_variedad_carne.jpeg"
    },

    {
        nombre: "Juguetes",
        descripcion: "Juguetes para mascotas.",
        imagen: RUTA_PRODUCTOS + "juguetes.png"
    },

    {
        nombre: "Kit de aseo profesional",
        descripcion: "Kit completo para el cuidado de tu mascota.",
        imagen: RUTA_PRODUCTOS + "Kit_de_aseo_profesional.jpg"
    },

    {
        nombre: "Shampoo control de olores",
        descripcion: "Shampoo para eliminar malos olores.",
        imagen: RUTA_PRODUCTOS + "Shampoo_control_de_olores.jpg"
    },

    {
        nombre: "Shampoo hidratante",
        descripcion: "Shampoo hidratante para mascotas.",
        imagen: RUTA_PRODUCTOS + "Shampoo_hidratante.jpeg"
    },

    {
        nombre: "Shampoo para cachorros",
        descripcion: "Shampoo especial para cachorros.",
        imagen: RUTA_PRODUCTOS + "Shampoo_para_cachorros.jpg"
    },

    {
        nombre: "Shampoo para pelo blanco",
        descripcion: "Shampoo para mascotas de pelo blanco.",
        imagen: RUTA_PRODUCTOS + "Shampoo_para_pelo_blanco.jpg"
    },

    {
        nombre: "Shampoo repelente de parásitos",
        descripcion: "Protección contra pulgas y garrapatas.",
        imagen: RUTA_PRODUCTOS + "Shampoo_repelente_de_parásitos.jpeg"
    },

    {
        nombre: "Shampoo",
        descripcion: "Shampoo para mascotas.",
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


    // Al presionar Enter baja hasta los productos

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