USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Dms_Comm_Info_M]    Script Date: 2022-02-11 ¿ÀÀü 9:34:31 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Dms_Comm_Info_M](
	[Inst_Name] [varchar](100) NOT NULL,
	[Task_Name] [varchar](100) NOT NULL,
	[Table_Name] [varchar](100) NOT NULL,
	[Identifier_Name] [varchar](100) NOT NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Dms_Comm_Info_M] PRIMARY KEY CLUSTERED 
(
	[Inst_Name] ASC,
	[Task_Name] ASC,
	[Table_Name] ASC,
	[Identifier_Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TB_Dms_Comm_Info_M] ADD  DEFAULT ('Not Assigned') FOR [Table_Name]
GO

ALTER TABLE [dbo].[TB_Dms_Comm_Info_M] ADD  DEFAULT ('Not Assigned') FOR [Identifier_Name]
GO


