// Orquestación general: pestañas, logout, inicialización y refresco automático.

      async function logout() {
        try {
          await fetch("/admin/logout");
          window.location.href = "/admin/login";
        } catch (error) {
          console.error(error);
          window.location.href = "/admin/login";
        }
      }

      // ==========================================================
      // PESTAÑAS
      // ==========================================================
      let vistaActual = "pedidos";

      function cambiarVista(vista) {
        vistaActual = vista;
        document.getElementById("vistaPedidos").style.display =
          vista === "pedidos" ? "block" : "none";
        document.getElementById("vistaProductos").style.display =
          vista === "productos" ? "block" : "none";
        document
          .getElementById("tabPedidos")
          .classList.toggle("activo", vista === "pedidos");
        document
          .getElementById("tabProductos")
          .classList.toggle("activo", vista === "productos");

        if (vista === "productos") {
          cargarProductos();
          cargarEstadoNegocio();
        }
      }

      function actualizarVistaActiva() {
        if (vistaActual === "pedidos") {
          cargarPedidos();
        } else {
          cargarProductos();
          cargarEstadoNegocio();
        }
      }

      // Inicializar
      cargarPedidos();

      // Recargar la vista activa cada 30 segundos
      setInterval(() => {
        actualizarVistaActiva();
      }, 30000);
