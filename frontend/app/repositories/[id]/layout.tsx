import MainLayout from "@/app/components/layout/MainLayout";

export default function RepositoryLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <MainLayout>{children}</MainLayout>;
}
