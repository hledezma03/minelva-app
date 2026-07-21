// Estado del negocio: abierto / cerrado.

      // ==========================================================
      // ESTADO DEL NEGOCIO (abierto / cerrado)
      // ==========================================================
      function onCambiarSwitchAbierto() {
        const abierto = document.getElementById("switchAbierto").checked;
        document.getElementById("labelEstadoNegocio").textContent = abierto
          ? "Negocio abierto"
          : "Negocio cerrado";
        document.getElementById("inputMensajeCierre").style.display = abierto
          ? "none"
          : "block";
      }

      async function cargarEstadoNegocio() {
        try {
          const response = await fetch("/admin/estado-negocio");
          const data = await response.json();
          if (data.error) return;

          const estado = data.estado || { abierto: true, mensaje: "" };
          document.getElementById("switchAbierto").checked = !!estado.abierto;
          document.getElementById("inputMensajeCierre").value =
            estado.mensaje || "";
          onCambiarSwitchAbierto();
        } catch (error) {
          console.error(error);
        }
      }

      async function guardarEstadoNegocio() {
        const abierto = document.getElementById("switchAbierto").checked;
        const mensaje = document
          .getElementById("inputMensajeCierre")
          .value.trim();

        try {
          const response = await fetch("/admin/estado-negocio", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ abierto, mensaje }),
          });
          const data = await response.json();
          if (data.error) {
            alert(data.error);
            return;
          }
          alert(
            "✅ Estado del negocio actualizado. El chatbot ya lo tiene en cuenta.",
          );
        } catch (error) {
          console.error(error);
          alert("Error de conexión al guardar el estado");
        }
      }
