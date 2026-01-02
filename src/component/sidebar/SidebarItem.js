import { NavLink } from "react-router-dom";

const SidebarItem = ({ label, icon, to, isCollapsed }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 p-3 rounded-lg transition
        ${isActive ? "bg-blue-100 text-blue-600" : "hover:bg-gray-200"}`
      }
    >
      <span className="text-lg">{icon}</span>
      {!isCollapsed && <span>{label}</span>}
    </NavLink>
  );
};

export default SidebarItem;
