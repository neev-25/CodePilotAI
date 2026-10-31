import {
    LayoutDashboard,
    FolderGit2,
    BarChart3,
    Search,
    Network,
    Settings,
    User,
} from "lucide-react";

export const navigation = [

    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
    },

    {
        title: "Repositories",
        href: "/repositories",
        icon: FolderGit2,
    },

    {
        title: "Project Analysis",
        href: "/analysis",
        icon: BarChart3,
    },

    {
        title: "Code Q&A",
        href: "/search",
        icon: Search,
    },

    {
        title: "Architecture",
        href: "/architecture",
        icon: Network,
    },

    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
    },

    {
        title: "Profile",
        href: "/profile",
        icon: User,
    },

];