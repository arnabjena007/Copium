"use client";

const productLinks = [
  { label: "Features", href: "#features" },
  { label: "Anomaly Dashboard", href: "http://localhost:8501" },
  { label: "Pricing", href: "#" },
  { label: "Changelog", href: "#" },
  { label: "Roadmap", href: "#" },
];

const integrationLinks = [
  { label: "AWS EC2", href: "#" },
  { label: "AWS S3", href: "#" },
  { label: "AWS Lambda", href: "#" },
  { label: "AWS RDS", href: "#" },
  { label: "AWS CloudWatch", href: "#" },
];

const resourceLinks = [
  { label: "Documentation", href: "#" },
  { label: "API Reference", href: "#" },
  { label: "Live Audit Engine", href: "http://localhost:8501" },
  { label: "Status Page", href: "#" },
  { label: "Blog", href: "#" },
];

const companyLinks = [
  { label: "About", href: "#" },
  { label: "Careers", href: "#" },
  { label: "Press Kit", href: "#" },
  { label: "Security", href: "#" },
  { label: "Contact", href: "#" },
];

export function Footer() {
  return (
    <footer className="relative z-10 w-full bg-white border-t border-slate-200">
      
      {/* Top section: Brand + newsletter */}
      <div className="max-w-6xl mx-auto px-6 md:px-10 pt-16 pb-12 flex flex-col md:flex-row justify-between gap-10">
        
        {/* Brand */}
        <div className="max-w-xs">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-9 h-9 rounded-xl bg-brand-teal flex items-center justify-center shadow-lg shadow-teal-100">
              <span className="text-white font-black text-base leading-none">A</span>
            </div>
            <span className="font-extrabold text-brand-slate text-xl tracking-tight">Anomaly Engine</span>
          </div>
          <p className="text-slate-500 text-sm leading-relaxed mb-6">
            The automated FinOps command center for engineering teams spending on AWS. Identify waste, prevent overruns, and maintain control.
          </p>
          <div className="flex items-center gap-3">
            {/* Social icons */}
            {[
              { name: "X", href: "#" },
              { name: "GH", href: "#" },
              { name: "LI", href: "#" },
            ].map((s) => (
              <a
                key={s.name}
                href={s.href}
                className="w-9 h-9 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 text-xs font-bold hover:border-brand-teal hover:text-brand-teal transition-all duration-150 shadow-sm"
              >
                {s.name}
              </a>
            ))}
          </div>
        </div>

        {/* Newsletter CTA */}
        <div className="max-w-sm w-full">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Stay updated</p>
          <h4 className="text-brand-slate font-bold text-lg mb-4">
            FinOps tips and product updates to your inbox.
          </h4>
          <div className="flex gap-2">
            <input
              type="email"
              placeholder="you@company.com"
              autoComplete="off"
              className="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-brand-slate placeholder-slate-400 focus:outline-none focus:border-brand-teal transition-colors"
            />
            <button className="bg-brand-teal text-white font-bold px-5 py-2.5 rounded-xl text-sm hover:bg-brand-teal-dark transition-colors shadow-md shadow-teal-50 whitespace-nowrap">
              Subscribe
            </button>
          </div>
          <p className="text-slate-400 text-xs mt-2">No spam. Unsubscribe anytime.</p>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-slate-200" />

      {/* Link columns */}
      <div className="max-w-6xl mx-auto px-6 md:px-10 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
        {[
          { title: "Product", links: productLinks },
          { title: "Integrations", links: integrationLinks },
          { title: "Resources", links: resourceLinks },
          { title: "Company", links: companyLinks },
        ].map(({ title, links }) => (
          <div key={title}>
            <h4 className="text-[0.65rem] font-extrabold text-slate-400 uppercase tracking-[0.15em] mb-5">
              {title}
            </h4>
            <ul className="space-y-3">
              {links.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-slate-600 text-sm hover:text-brand-teal transition-colors duration-150 font-medium"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Divider */}
      <div className="border-t border-slate-200" />

      {/* Copyright bar */}
      <div className="max-w-6xl mx-auto px-6 md:px-10 py-6 flex flex-col md:flex-row items-center justify-between gap-3">
        <p className="text-slate-400 text-sm text-center md:text-left">
          © {new Date().getFullYear()}{" "}
          <span className="font-semibold text-brand-slate">Anomaly Engine, Inc.</span>{" "}
          All rights reserved. Built to eliminate cloud waste.
        </p>
        <div className="flex items-center gap-6">
          {["Privacy Policy", "Terms of Service", "Cookie Policy"].map((item) => (
            <a
              key={item}
              href="#"
              className="text-slate-400 text-xs hover:text-brand-slate transition-colors font-medium"
            >
              {item}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}
