const API = "https://univrs-general-api.ue.r.appspot.com"

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API}/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("user", JSON.stringify(data.user))
            await fetch("/set_cookies", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ token: data.token })
            });

            // El servidor Flask ahora tiene el token, puede renderizar según rol
            window.location.href = "/";

        } else {
            alert(data.error || "Login failed");
        }

    } catch (error) {
        console.error("Error durante el login:", error);
        alert("Error de conexión. Inténtalo de nuevo.");
    }
});




