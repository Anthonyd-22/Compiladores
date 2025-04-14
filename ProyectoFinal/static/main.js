let user;
let modalContainer;
let editReservationModal;
let editUserModal;

function editReservation() {
    editReservationModal.show();
}

function editUser(modal) {
    modal.show();
}

async function editUserForm(userId, payload) {
    try {
        const response = await fetch(`/api_proxy/users/${userId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: 'include',
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            const data = await response.json();
            if (data.updated_user.id === JSON.parse(localStorage.getItem("user")).id) {
                console.log("Current user updated his information");
                localStorage.removeItem("user");
                localStorage.setItem("user", JSON.stringify(data.updated_user));
            }
            alert(data.message);
            location.reload(); // O recarga solo la lista de usuarios
        } else {
            alert(response.error || "Error al actualizar usuario");
        }
    } catch (error) {
        console.error("Error al actualizar usuario:", error);
        alert("Error de conexión.");
    }
}


async function deleteReservation(reservationId) {
    if (!confirm("¿Estás seguro de que deseas eliminar esta reservación?")) return;


    try {
        const response = await fetch(`/api_proxy/reservations/${reservationId}`, {
            method: "DELETE",
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            alert("Reservación eliminada con éxito");
            location.reload(); // Recargar la tabla
        } else {
            alert(data.error || "Error al eliminar reservación");
        }
    } catch (error) {
        console.error("Error al eliminar reservación:", error);
        alert("Error de conexión.");
    }
}

async function deleteUser(userId) {

    if (!confirm("¿Estás seguro de eliminar este usuario?")) return;

    const response = await fetch(`/api_proxy/users/${userId}`, {
        method: "DELETE",
        credentials: 'include'
    });

    const result = await response.json();
    if (response.ok) {
        alert("Usuario eliminado correctamente");
        location.reload();
    } else {
        alert("Error al eliminar usuario: " + result.error);
    }

    return result;
}


function dropSession() {
    localStorage.removeItem("user");
    window.location.href = "/logout";
}


document.addEventListener("DOMContentLoaded", async () => {
    user = JSON.parse(localStorage.getItem("user"))
    const userNameTag = document.getElementById("user-name");
    userNameTag.innerHTML = user.name.split(" ")[0];
    const signOut = document.getElementById("sign-out");
    const closeSession = document.getElementById("close-session");
    modalContainer = document.getElementById("modal-container");
    editReservationModal = new bootstrap.Modal(document.getElementById("edit-reservation-modal"));
    editUserModal = new bootstrap.Modal(document.getElementById("edit-user-modal"));

    signOut.addEventListener("click", function () {
        dropSession();
    });
    closeSession.addEventListener("click", function () {
        dropSession();
    })

    function updateTabVisibility() {
        setTimeout(() => { // Esperamos para que Bootstrap termine su transición
            const activePane = document.querySelector(".tab-pane.show.active");

            if (activePane) {
                document.querySelectorAll(".tab-pane").forEach(pane => {
                    if (pane === activePane) {
                        pane.classList.add("d-flex");  // Asegurar que se muestre
                        pane.classList.remove("d-none");
                    } else {
                        pane.classList.add("d-none");  // Ocultar los demás
                        pane.classList.remove("d-flex");
                    }
                });
            } else {
                console.warn("No se encontró ninguna pestaña activa. Esperando...");
            }
        }, 175); // Pequeño delay para esperar a Bootstrap
    }

    // Escucha cambios en los tabs
    document.querySelectorAll('[data-bs-toggle="list"]').forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (event) {
            // console.log(`🔄 Cambio de pestaña a: ${event.target.getAttribute("href")}`);
            updateTabVisibility();
        });
    });
    updateTabVisibility();

    const usersTableBody = document.getElementById("users-table-body");
    const reservationsTableBody = document.getElementById("reservations-table-body");
    const userReservationsTableBody = document.getElementById("user-reservations-table-body");



    async function fetchData(endpoint, tableBody, renderFunction) {
        try {
            const response = await fetch(`/api_proxy/${endpoint}`, {
                credentials: 'include'
            });
            const data = await response.json();
            tableBody.innerHTML = "";
            data.forEach(renderFunction);
        } catch (error) {
            console.error(`Error cargando ${endpoint}:`, error);
        }
    }

    function renderUser(user) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>
                <button class="btn btn-warning btn-sm edit-user-btn" data-user-id="${user.id}">Editar</button>
                <button class="btn btn-danger btn-sm delete-user-btn" data-user-id="${user.id}">Eliminar</button>
            </td>
        `;
        usersTableBody.appendChild(row);
    }


    function renderReservation(reservation, tableBody) {
    const row = document.createElement("tr");
    const date = new Date(reservation.appointment_date);
    const formattedDate = date.toLocaleString("es-ES", {
        day: "2-digit", month: "2-digit", year: "numeric",
        hour: "2-digit", minute: "2-digit"
    });

    row.innerHTML = `
        <td>${reservation.id}</td>
        <td>${reservation.user_id}</td>
        <td>${reservation.appointment_name}</td>
        <td>${formattedDate}</td>
        <td>${reservation.status}</td>
        <td>${reservation.notes}</td>
        <td>
            <button class="btn btn-warning btn-sm edit-reservation-btn" data-reservation-id="${reservation.id}">Editar</button>
            <button class="btn btn-danger btn-sm delete-reservation-btn" data-reservation-id="${reservation.id}">Eliminar</button>
        </td>
    `;
    tableBody.appendChild(row);
    }


    if (!user) {
        alert("No se encontró información del usuario.");
        return;
    }

    document.getElementById("user-name-tag").textContent = user.name || "N/A";
    document.getElementById("user-email-tag").textContent = user.email || "N/A";
    document.getElementById("user-role-tag").textContent = user.role || "N/A";

    const date = new Date(user.created_at);
    const formattedDate = date.toLocaleDateString("es-ES", {
        day: "2-digit", month: "2-digit", year: "numeric"
    });

    document.getElementById("user-registration-date").textContent = formattedDate;



    await fetchData("users", usersTableBody, renderUser);
    await fetchData(`reservations`, reservationsTableBody, (r) => renderReservation(r, reservationsTableBody));
    await fetchData(`reservations/user/${user.id}`, userReservationsTableBody, (r) => renderReservation(r, userReservationsTableBody));

});


document.getElementById("create-user-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("user-name-form").value;
    const email = document.getElementById("user-email").value;
    const password = document.getElementById("user-password").value;
    const role = document.getElementById("user-role").value;


    try {
        const response = await fetch(`/api_proxy/users`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: 'include',
            body: JSON.stringify({name, email, password, role})
        });

        const data = await response.json();

        if (response.ok) {
            alert("Usuario creado con éxito");
            document.getElementById("create-user-form").reset();
        } else {
            alert(data.error || "Error al crear usuario");
        }
    } catch (error) {
        console.error("Error al crear usuario:", error);
        alert("Error de conexión");
    }
});

document.getElementById("create-reservation-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const appointment_name = document.getElementById("appointment-name").value;
    const appointment_date = document.getElementById("appointment-date").value;
    const notes = document.getElementById("notes").value;


    try {
        const response = await fetch(`/api_proxy/reservations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: 'include',
            body: JSON.stringify({
                appointment_name,
                appointment_date,
                notes
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Reservación creada con éxito");
            document.getElementById("create-reservation-form").reset();
            location.reload();
        } else {
            alert(data.error || "Error al crear reservación");
        }
    } catch (error) {
        console.error("Error al crear reservación:", error);
        alert("Error de conexión");
    }
});

document.getElementById("edit-reservation-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const reservationId = document.getElementById("edit-reservation-id").value;
    const appointment_name = document.getElementById("edit-appointment-name").value;
    const appointment_date = document.getElementById("edit-appointment-date").value;
    const notes = document.getElementById("edit-notes").value;
    const status = document.getElementById("edit-status").value;


    try {
        const response = await fetch(`/api_proxy/reservations/${reservationId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: 'include',
            body: JSON.stringify({
                appointment_name,
                appointment_date,
                notes,
                status
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Reservación actualizada con éxito");
            location.reload(); // Recargar la tabla
        } else {
            alert(data.error || "Error al actualizar reservación");
        }
    } catch (error) {
        console.error("Error al actualizar reservación:", error);
        alert("Error de conexión.");
    }
});

document.getElementById("edit-user-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("edit-user-name").value;
    const email = document.getElementById("edit-user-email").value;
    const password = document.getElementById("edit-user-password").value;
    let role = document.getElementById("edit-user-role");
    let user_id = document.getElementById("form-user-id").textContent;
    const payload = {name, email, role};
    if (password) {
        payload.password = password;
    }
    if (!user_id) {
        user_id = JSON.parse(localStorage.getItem("user")).id;
    }
    if (!role){
        payload.role = "user";
    } else {
        payload.role = role.value;
    }
    await editUserForm(user_id, payload);
});


document.addEventListener("click", function (e) {
    if (e.target.matches(".edit-reservation-btn")) {
        editReservation();
    }
    if (e.target.matches(".delete-reservation-btn")) {
        const id = e.target.getAttribute("data-reservation-id");
        deleteReservation(id).then(r => console.log("Delete reservation function executed"));
    }
    if (e.target.matches(".edit-user-btn")) {
        const userIdTag = document.getElementById("form-user-id");
        userIdTag.innerHTML = e.target.getAttribute("data-user-id");
        userIdTag.classList.add("d-none");
        editUser(editUserModal);
    }
    if (e.target.matches(".delete-user-btn")) {
        const id = e.target.getAttribute("data-user-id");
        deleteUser(id).then(r => console.log("Delete user function executed"));
    }
    if (e.target.matches(".edit-current-user")) {
        editUser(editUserModal);
    }
});

