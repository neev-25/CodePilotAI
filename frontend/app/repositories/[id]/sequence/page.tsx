import DiagramReport from "@/app/components/repository/reports/DiagramReport";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function SequenceDiagramPage({ params }: Props) {
  const { id } = await params;
  return <DiagramReport repoId={Number(id)} kind="sequence" />;
}
