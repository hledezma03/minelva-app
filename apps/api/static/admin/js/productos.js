// Gestión de productos y precios: listar, crear, editar, eliminar.

      // ==========================================================
      // PRODUCTOS Y PRECIOS
      // ==========================================================
      let productoEditandoId = null;

      async function cargarProductos() {
        const container = document.getElementById("productosTable");
        container.innerHTML =
          '<div class="loading">🛒 Cargando productos...</div>';

        try {
          const response = await fetch("/admin/productos");
          const data = await response.json();

          if (data.auth_required === true || data.error === "No autorizado") {
            window.location.href = "/admin/login";
            return;
          }
          if (data.error) {
            container.innerHTML = `<div class="empty-state">❌ Error: ${data.error}</div>`;
            return;
          }

          const productos = data.productos || [];
          if (productos.length === 0) {
            container.innerHTML =
              '<div class="empty-state">📭 No hay productos registrados. Agrega el primero arriba.</div>';
            return;
          }

          container.innerHTML = `
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th>Precio</th>
                  <th>Disponible</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                ${productos
                  .map(
                    (p) => `
                  <tr class="${p.disponible ? "" : "producto-no-disponible"}">
                    <td>
                      <strong>${escapeHtml(p.nombre)}</strong><br>
                      <small style="color:#888">${escapeHtml(p.descripcion || "")}</small>
                    </td>
                    <td>${escapeHtml(p.categoria || "general")}</td>
                    <td>$${Number(p.precio).toFixed(2)}</td>
                    <td>${p.disponible ? "✅ Sí" : "🚫 No"}</td>
                    <td>
                      <button class="btn-editar" title="Editar" onclick='mostrarFormularioProducto(${JSON.stringify(p)})'>✏️</button>
                      <button class="btn-eliminar" title="Eliminar" onclick="eliminarProducto('${p.id_producto}')">🗑️</button>
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
            '<div class="empty-state">❌ Error al cargar los productos</div>';
        }
      }

      function mostrarFormularioProducto(producto) {
        productoEditandoId = producto ? producto.id_producto : null;
        const contenedor = document.getElementById("formProductoContenedor");

        contenedor.innerHTML = `
          <div class="form-producto">
            <div>
              <label>Nombre</label>
              <input type="text" id="fpNombre" value="${producto ? escapeHtml(producto.nombre) : ""}" required>
            </div>
            <div>
              <label>Descripción</label>
              <input type="text" id="fpDescripcion" value="${producto ? escapeHtml(producto.descripcion || "") : ""}">
            </div>
            <div>
              <label>Precio ($)</label>
              <input type="number" id="fpPrecio" step="0.01" min="0" value="${producto ? producto.precio : ""}" required>
            </div>
            <div>
              <label>Categoría</label>
              <input type="text" id="fpCategoria" value="${producto ? escapeHtml(producto.categoria || "general") : "general"}">
            </div>
            <div>
              <label>Orden</label>
              <input type="number" id="fpOrden" value="${producto ? producto.orden || 0 : 0}">
            </div>
            <div>
              <label>Disponible</label>
              <select id="fpDisponible">
                <option value="true" ${!producto || producto.disponible ? "selected" : ""}>Sí</option>
                <option value="false" ${producto && !producto.disponible ? "selected" : ""}>No</option>
              </select>
            </div>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-guardar" onclick="guardarProducto()">💾 Guardar</button>
              <button class="btn btn-cancelar" onclick="cerrarFormularioProducto()">✖️ Cancelar</button>
            </div>
          </div>
        `;
        contenedor.scrollIntoView({ behavior: "smooth", block: "center" });
      }

      function cerrarFormularioProducto() {
        productoEditandoId = null;
        document.getElementById("formProductoContenedor").innerHTML = "";
      }

      async function guardarProducto() {
        const body = {
          nombre: document.getElementById("fpNombre").value.trim(),
          descripcion: document.getElementById("fpDescripcion").value.trim(),
          precio: parseFloat(document.getElementById("fpPrecio").value),
          categoria:
            document.getElementById("fpCategoria").value.trim() || "general",
          orden: parseInt(document.getElementById("fpOrden").value) || 0,
          disponible: document.getElementById("fpDisponible").value === "true",
        };

        if (!body.nombre || isNaN(body.precio)) {
          alert("Nombre y precio son obligatorios");
          return;
        }

        try {
          const url = productoEditandoId
            ? `/admin/productos/${productoEditandoId}`
            : "/admin/productos";
          const metodo = productoEditandoId ? "PUT" : "POST";

          const response = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          const data = await response.json();

          if (data.error) {
            alert(data.error);
            return;
          }

          cerrarFormularioProducto();
          cargarProductos();
        } catch (error) {
          console.error(error);
          alert("Error de conexión al guardar el producto");
        }
      }

      async function eliminarProducto(productoId) {
        if (
          !confirm("⚠️ ¿Eliminar este producto? Ya no aparecerá en el chatbot.")
        )
          return;

        try {
          const response = await fetch(`/admin/productos/${productoId}`, {
            method: "DELETE",
          });
          const data = await response.json();
          if (data.error) {
            alert(data.error);
            return;
          }
          cargarProductos();
        } catch (error) {
          console.error(error);
          alert("Error de conexión al eliminar el producto");
        }
      }
