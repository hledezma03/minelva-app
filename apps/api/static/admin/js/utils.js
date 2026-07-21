// Utilidades compartidas por los distintos módulos del panel admin.

      function normalizarNombreProducto(texto) {
        if (!texto) return "Producto";
        const t = texto.toLowerCase().replace(/[_]/g, " ").trim();

        const catalogo = [
          [/recarga/, "Recarga"],
          [/delivery/, "Delivery"],
          [/20\s*l.*rosca|rosca.*20/, "Botellón 20L tapa rosca"],
          [/20\s*l.*normal|normal.*20/, "Botellón 20L normal"],
          [/12\s*l/, "Botellón 12L"],
          [/asa/, "Botellón con asa y rosca"],
          [/dispensador/, "Dispensador manual"],
          [/hielo/, "Hielo"],
        ];
        for (const [patron, nombreBonito] of catalogo) {
          if (patron.test(t)) return nombreBonito;
        }

        // Si no coincide con el catálogo conocido, al menos separamos
        // palabras pegadas a números (ej: "botellon20l" -> "botellon 20 l")
        // para que no se vea como una sola palabra ilegible.
        return texto
          .replace(/_/g, " ")
          .replace(/([a-záéíóúñ])(\d)/gi, "$1 $2")
          .replace(/(\d)([a-záéíóúñ])/gi, "$1 $2")
          .replace(/\s+/g, " ")
          .trim();
      }

      function formatearProductos(productos, cantidadPedido) {
        if (!productos) return "Sin productos";

        try {
          let productosArray;
          if (typeof productos === "string") {
            productosArray = JSON.parse(productos);
          } else {
            productosArray = productos;
          }

          if (!Array.isArray(productosArray) || productosArray.length === 0) {
            return "Sin productos";
          }

          const lineas = [];
          productosArray.forEach((p) => {
            const nombreCrudo = p.nombre || p.producto || "Producto";

            // FIX: en versiones anteriores, la IA a veces combinaba varios
            // productos dentro de un mismo campo "nombre" separados por
            // coma o punto y coma (ej: "2 botellon 20L, 1 hielo"). Antes
            // esto se mostraba tal cual, pegado y feo. Ahora separamos
            // cada producto y lo mostramos en su propia línea.
            const fragmentos = nombreCrudo
              .split(/[,;]+/)
              .map((f) => f.trim())
              .filter(Boolean);

            fragmentos.forEach((frag) => {
              const match = frag.match(/^(\d+)\s*x?\s*(.+)$/i);
              if (match) {
                lineas.push(
                  `${match[1]} x ${normalizarNombreProducto(match[2])}`,
                );
              } else if (/^\d+$/.test(frag)) {
                // Fragmento que es solo un número suelto (residuo de un
                // formato mal separado): lo ignoramos, no aporta info.
                return;
              } else {
                const cantidad =
                  fragmentos.length === 1
                    ? p.cantidad || cantidadPedido || 1
                    : 1;
                lineas.push(`${cantidad} x ${normalizarNombreProducto(frag)}`);
              }
            });
          });

          return lineas.length > 0 ? lineas.join("<br>") : "Sin productos";
        } catch (e) {
          return escapeHtml(String(productos));
        }
      }

      function getEstadoClass(estado) {
        switch (estado) {
          case "pendiente":
            return "estado-pendiente";
          case "pagado":
            return "estado-pagado";
          case "entregado":
            return "estado-entregado";
          case "cancelado":
            return "estado-cancelado";
          default:
            return "";
        }
      }

      function escapeHtml(text) {
        if (!text) return "";
        return text.replace(/[&<>]/g, function (m) {
          if (m === "&") return "&amp;";
          if (m === "<") return "&lt;";
          if (m === ">") return "&gt;";
          return m;
        });
      }
