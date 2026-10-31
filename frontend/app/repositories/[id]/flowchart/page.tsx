import DiagramReport from "@/app/components/repository/reports/DiagramReport";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function FlowchartPage({ params }: Props) {
  const { id } = await params;
  return <DiagramReport repoId={Number(id)} kind="flowchart" />;
}
