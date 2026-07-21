// Gestión de pedidos: cargar, cambiar estado, eliminar.

      async function cargarPedidos() {
        const container = document.getElementById("pedidosTable");
        container.innerHTML =
          '<div class="loading">📦 Cargando pedidos...</div>';

        try {
          const response = await fetch("/admin/pedidos");
          const data = await response.json();

          if (data.auth_required === true || data.error === "No autorizado") {
            window.location.href = "/admin/login";
            return;
          }

          if (data.error) {
            container.innerHTML = `<div class="empty-state">❌ Error: ${data.error}</div>`;
            return;
          }

          const pedidos = data.pedidos || [];

          // Actualizar estadísticas
          const stats = {
            total: pedidos.length,
            pendiente: pedidos.filter((p) => p.estado === "pendiente").length,
            pagado: pedidos.filter((p) => p.estado === "pagado").length,
            entregado: pedidos.filter((p) => p.estado === "entregado").length,
          };

          document.getElementById("stats").innerHTML = `
                    <div class="stat-card">
                        <h3>📦 Total Pedidos</h3>
                        <div class="number">${stats.total}</div>
                    </div>
                    <div class="stat-card">
                        <h3>⏳ Pendientes</h3>
                        <div class="number">${stats.pendiente}</div>
                    </div>
                    <div class="stat-card">
                        <h3>💰 Pagados</h3>
                        <div class="number">${stats.pagado}</div>
                    </div>
                    <div class="stat-card">
                        <h3>✅ Entregados</h3>
                        <div class="number">${stats.entregado}</div>
                    </div>
                `;

          if (pedidos.length === 0) {
            container.innerHTML =
              '<div class="empty-state">📭 No hay pedidos registrados</div>';
            return;
          }

          container.innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>Cliente</th>
                                <th>Dirección</th>
                                <th>Teléfono</th>
                                <th>Productos</th>
                                <th>Estado</th>
                                <th>Fecha</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${pedidos
                              .map(
                                (p) => `
                                <tr>
                                    <td><strong>${escapeHtml(p.nombre_cliente)}</strong></td>
                                    <td>${escapeHtml(p.direccion_entrega)}</td>
                                    <td>${p.telefono_contacto}</td>
                                    <td>${formatearProductos(p.productos, p.cantidad_total)}</td>
                                    <td>
                                        <select onchange="cambiarEstado('${p.id_pedido}', this.value)">
                                            <option value="pendiente" ${p.estado === "pendiente" ? "selected" : ""}>⏳ Pendiente</option>
                                            <option value="pagado" ${p.estado === "pagado" ? "selected" : ""}>💰 Pagado</option>
                                            <option value="entregado" ${p.estado === "entregado" ? "selected" : ""}>✅ Entregado</option>
                                            <option value="cancelado" ${p.estado === "cancelado" ? "selected" : ""}>❌ Cancelado</option>
                                        </select>
                                    </td>
                                    <td>${p.fecha_creacion ? new Date(p.fecha_creacion).toLocaleDateString() : "N/A"}</td>
                                    <td>
                                        <button class="btn-eliminar" onclick="eliminarPedido('${p.id_pedido}')" title="Eliminar pedido">🗑️</button>
                                    </td>
                                </tr>
                            `,
                              )
                              .join("")}
                        </tbody>
                    </table>
                `;
        } catch (error) {
          console.error(error);
          container.innerHTML =
            '<div class="empty-state">❌ Error al cargar los pedidos</div>';
        }
      }

      async function cambiarEstado(pedidoId, nuevoEstado) {
        try {
          const response = await fetch(
            `/admin/pedidos/${pedidoId}/estado?estado=${nuevoEstado}`,
            {
              method: "PUT",
            },
          );

          if (response.ok) {
            cargarPedidos();
          } else {
            const data = await response.json();
            alert(data.error || "Error al actualizar el estado");
          }
        } catch (error) {
          console.error(error);
          alert("Error de conexión");
        }
      }

      async function eliminarPedido(pedidoId) {
        if (
          !confirm(
            "⚠️ ¿Eliminar este pedido permanentemente? Esta acción no se puede deshacer.",
          )
        )
          return;

        try {
          const response = await fetch(`/admin/pedidos/${pedidoId}`, {
            method: "DELETE",
          });

          if (response.ok) {
            cargarPedidos();
          } else {
            const data = await response.json();
            alert(data.error || "Error al eliminar el pedido");
          }
        } catch (error) {
          console.error(error);
          alert("Error de conexión");
        }
      }
