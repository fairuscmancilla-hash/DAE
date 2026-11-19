// Footer receives the contact object from App.
export default function Footer({ contact }) {
  return (
    <footer className="site-footer" id="contacto">
      <div>
        <h2>Contacto</h2>
        <p>{contact.address}</p>
        <p>{contact.hours}</p>
      </div>
      <div>
        <p>
          <a href={`tel:${contact.phone}`}>{contact.phone}</a>
        </p>
        <p>
          <a href={`mailto:${contact.email}`}>{contact.email}</a>
        </p>
      </div>
    </footer>
  );
}
